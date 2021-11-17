import requests
import emoji
from bs4 import  Tag, BeautifulSoup
import os

# get secrets from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
MAINTAINER_CHATID = os.environ.get("MAINTAINER_CHATID")
MACHINE_NAME = os.environ.get("MACHINE_NAME")

def emojify(tag, meal):
  """This function returns the meal wrapped in three emojis using the specified tag"""
  return "".join([tag]*3)+ meal + "".join([tag]*3)

def get_heading(meal):
  """This function returns a formatted heading with different emojis depending on content of meal"""
  
  if "fisch" in meal.lower():
    return emojify(":fish:", meal) 
  elif "fleisch" in meal.lower(): 
    return emojify(":shallow_pan_of_food:", meal) 
  elif "vegetarisch" in meal.lower(): 
    return emojify(":falafel:", meal) 
  elif "vegan" in meal.lower():
    return emojify(":broccoli:", meal) 
  elif "pizza" in meal.lower():
    return emojify(":pizza:", meal) 
  elif "wok" in meal.lower(): 
    return emojify(":curry_rice:", meal) 
  elif "smoothie" in meal.lower(): 
    return emojify(":tropical_drink:", meal) 
  elif "salat" in meal.lower(): 
    return emojify(":green_salad:", meal) 
  elif "grill" in meal.lower(): 
    return emojify(":fire:", meal)    
  elif "pasta" in meal.lower(): 
    return emojify(":spaghetti:", meal)      
  elif "sättigung" in meal.lower(): 
    return emojify(":french_fries:", meal)      
  elif "suppe" in meal.lower(): 
    return emojify(":bowl_with_spoon:", meal)      
  else:
    return meal

    
def get_soup(url: str):
  """ Returns a Beautifulsoup object from a specified url."""
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  return soup

def clean_string(string_to_clean, to_remove):
  """Takes a string and cleans it from a list of strings and returns cleaned strin. """
  for ch in to_remove:
    string_to_clean = string_to_clean.replace(ch, "")
  return string_to_clean


def get_menu(soup):
  """Takes a soup object and extracts menu from it. Returns a dictionary with dishtype as keys and corresponding dishes and prices."""
  
  # find date by taking selected date in drop down
  date = soup.find_all("option", {"selected": "selected"})[1].text
  menucard = [tag for tag in list(soup.find_all("section", {"class": "meals"})[0]) if tag != "\n"][1:]
  
  # helper structures for saving menucard information
  meal = ""
  menu = {}

  # iterate over each tag in the menu section
  for tag in menucard:
      if isinstance(tag, Tag):
          # not all tags have attribute "class", so we go over alle values of attributes to search for specific tag
          attribute_values = list(*tag.attrs.values())
          
          if "title-prim" in attribute_values:
            # set the meal category 
              meal = tag.text
              if meal not in menu:
                  menu[meal] = {"subtitle": "", "meals":[]}
          
          elif "meals__subtitle" in attribute_values:
              menu[meal]["subtitle"] = tag.text
          
          elif "accordion" in attribute_values:
            # each accordion can hold multiple meals, saved in sections 
              items = tag.find_all("section")
            
            # extract information name, price and sidedish for each meal in the accordion
              for item in items: 
                  name = item.find("h4", {"class": "meals__name"}).text
                  price = clean_string(item.find("p", {"class": "meals__price"}).text, ["\n", " ", "Preise:"]).replace("/", "   ")
                  
                  # find all sidedish information
                  sides = item.find_all("li")
                  sidedishes = ""

                  # only execute if there are any sidedishes
                  if len(sides) > 0:
                      sidedishes += "mit "
                      for s in sides:
                          sidedishes += s.text + "\n"

                  # finally add our new meal to the corresponding meal category        
                  menu[meal]["meals"] += [f'{name}\n{sidedishes}{price}\n\n']

  return date, menu


def make_message(date, menu, mensa):
  """ Generates the final message that is send to telegram bot."""
  msg = ""
  msg += f"<b>{mensa}\n{date}\n\n</b>"
  if len(menu)==0:
    msg += "Kein Menü verfügbar."
    
  for key, value in menu.items():
    msg += f"\n<b>{get_heading(key)}</b>\n"
    if value["subtitle"] != "":
      msg += f"{value['subtitle']}\n"
    for meal in value["meals"]:
      
      # mensa campaigns in smoothie menu -.-
      if "Genießen" not in meal:
        msg += meal  

    # & breaks api trigger    
    msg = msg.replace("&", "und")
  return msg

def main():
  try:
    # generate soup and extract menu
    soup = get_soup('https://www.studentenwerk-leipzig.de/mensen-cafeterien/speiseplan?location=106')
    date, menu = get_menu(soup)
    # make message and emojize message
    msg = emoji.emojize(make_message(date, menu, "Mensa am Park"))
    
    # trigger telegram bot api
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHANNEL_ID}&text={msg}&parse_mode=html")
    
    # check if response is "ok", else raise exception and send response text
    if response.status_code != 200:
      raise Exception(f"Did not receive 200 from Telegram API.\n{response.text}")

  except Exception as e:

    # if script fails, send message to maintainer chat
    message = f"Feed Me Bot script failed on {MACHINE_NAME}.\nError Message:\n{str(e)}"
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={MAINTAINER_CHATID}&text={message}&parse_mode=html")


if __name__ == "__main__":
    main()