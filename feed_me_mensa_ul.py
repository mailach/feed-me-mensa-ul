import requests
import emoji
from bs4 import  Tag, BeautifulSoup
import os




# get secrets from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
MAINTAINER_CHATID = os.environ.get("MAINTAINER_CHATID")
MACHINE_NAME = os.environ.get("MACHINE_NAME")


def  get_feiertag(soup):
  months = {"Januar": "01", "Feburar": "02", "März": "03", "April": "04", "Mai": "05", "Juni":"06", "Juli": "07", "August": "08", "September": "09", "Oktober": "10", "November": "11", "Dezember": "12"}
  date = soup.findAll("div")[0].text.replace("\n", "").strip()
  weekday = soup.findAll("div")[1].text.replace("\n", "").strip()
  name = soup.findAll("div")[2].text.replace("\n", "").strip()
  day = date.split()[0].replace(".", "")
  month = [v for k,v in months.items() if k==date.split()[1]][0] 

  return({"name": name, "day": day,  "month": month, "date": date, "weekday": weekday})

def get_feiertage():
  answer = requests.get("https://www.schulferien.org/deutschland/feiertage/sachsen/").text
  soup = BeautifulSoup(answer).findAll("div", class_="contentbox")[0]
  return([get_feiertag(s) for s in soup.findAll("tr", class_="row_panel")])


def emojify(tag, meal):
  """This function returns the meal wrapped in three emojis using the specified tag"""
  return "".join([tag]*3)+ meal + "".join([tag]*3)

def create_heading(meal):
  """This function returns a formatted heading with different emojis depending on content of meal"""
  
  options = {"fisch": ":fish:", "fleisch": ":shallow_pan_of_food:", "vegetarisch": ":falafel:",
             "vegan": ":broccoli:", "pizza": ":pizza:", "suppe": ":bowl_with_spoon:", 
             "wok": ":curry_rice:", "smoothie":":tropical_drink:", "grill": ":fire:",
             "pasta": ":spaghetti:", "salat":":green_salad:", "sättigung": ":french_fries:"}
  
  meal_lower = meal.lower()

  for key, value in options.items():
    if key in meal_lower:
      return emojify(value, meal)

  return meal


def create_local_representation_of_website(url):
  """ Creates a local representation of the website as beautifulsoup object."""
  html_page = requests.get(url).text
  soup = BeautifulSoup(html_page, "html.parser")
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
    msg += f"\n<b>{create_heading(key)}</b>\n"
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
    soup = create_local_representation_of_website('https://www.studentenwerk-leipzig.de/mensen-cafeterien/speiseplan?location=106')
    date, menu = get_menu(soup)
    # make message and emojize message
    msg = emoji.emojize(make_message(date, menu, "Mensa am Park"))
    feiertage = get_feiertage()

    for tag in feiertage:
      if tag["month"] == date.split(".")[1]:
        if tag["day"] == date.split(".")[0]:
          raise Exception("Heute ist Feiertag: " + tag['name'])

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