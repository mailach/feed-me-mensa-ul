import requests
import bs4
import emoji
from bs4 import  Tag
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
MAINTAINER_TOKEN = os.environ.get("MAINTAINER_TOKEN")
MAINTAINER_CHATID = os.environ.get("MAINTAINER_CHATID")

def emojify(tag, meal):
  return "".join([tag]*3)+ meal + "".join([tag]*3)

def get_heading(meal):
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
    return emojify(":fire:", meal)     #poultry_leg
  elif "pasta" in meal.lower(): 
    return emojify(":spaghetti:", meal)     
  else:
    return meal

    
def get_soup(url):
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text)
    return soup

def get_menu(soup):
    date = soup.find_all("option", {"selected": "selected"})[1].text
    menucard = [tag for tag in list(soup.find_all("section", {"class": "meals"})[0]) if tag != "\n"][1:]
    meal = ""
    menu = {}
    for i in range(len(menucard)):
        tag = menucard[i]
        if isinstance(tag, Tag):
            if "title-prim" in list(*tag.attrs.values()):
                meal = tag.text
                if meal not in menu:
                    menu[meal] = {"subtitle": "", "meals":[]}
            if "meals__subtitle" in list(*tag.attrs.values()):
                menu[meal]["subtitle"] = tag.text
            if "accordion" in list(*tag.attrs.values()):
                items = tag.find_all("section")
                for item in items: 
                    name = item.find("h4", {"class": "meals__name"}).text
                    
                    price = item.find("p", {"class": "meals__price"}).text.replace("\n", "").replace(" ", "").replace("Preise:", "").replace("/", "   ")
                    sides = item.find_all("li")
                    sidedishes = ""
                    if len(sides) > 0:
                        sidedishes += "mit "
                        for s in sides:
                            sidedishes += s.text + "\n"
                    menu[meal]["meals"] += [f'{name}\n{sidedishes}{price}\n\n']

    return date, menu



def make_message(date, menu, mensa):
  msg = ""
  msg += f"<b>{mensa}\n{date}\n\n</b>"
    
  for key, value in menu.items():
    msg += f"\n<b>{get_heading(key)}</b>\n"
    if value["subtitle"] != "":
      msg += f"{value['subtitle']}\n"
    for meal in value["meals"]:
      if "Genießen" not in meal:
        msg += meal 
    msg = msg.replace("&", "und")
  return msg

try:
  soup = get_soup('https://www.studentenwerk-leipzig.de/mensen-cafeterien/speiseplan?location=106')
  date, menu = get_menu(soup)
  msg = emoji.emojize(make_message(date, menu, "Mensa am Park"))
  response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHANNEL_ID}&text={msg}&parse_mode=html")

except Exception as e:
  message = f"Feed Me Bot failed on reinlach machine.\nError Message:\n{str(e)}"
  response = requests.get(f"https://api.telegram.org/bot{MAINTAINER_TOKEN}/sendMessage?chat_id={MAINTAINER_CHATID}&text={message}&parse_mode=html")