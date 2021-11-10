from typing import overload
import requests
import bs4
import random
import emoji
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
MAINTAINER_TOKEN = os.environ.get("MAINTAINER_TOKEN")
MAINTAINER_CHATID = os.environ.get("MAINTAINER_CHATID")

try:

  fruits = ["watermelon", "grapes", "melon", "tangerine", "banana", "pineapple", "peach", "cherries", "strawberry"]
  food = ["hamburger", "taco", "sushi", "bacon","hot_dog", "shallow_pan_of_food", "burrito","stuffed_flatbread", "pretzel","green_salad", "falafel","spaghetti", "tamale"]


  def menue_mensa_am_park():
    message = ""
    response = requests.get('https://www.studentenwerk-leipzig.de/mensen-cafeterien/speiseplan?location=106')
    soup = bs4.BeautifulSoup(response.text)
    date = soup.find_all("option", {"selected": "selected"})[1].text
    menuecard = soup.find_all("section", {"class": "meals"})[0]
    meals = menuecard.find_all("div", {"class": "meals__summary"})
    message += f'{"".join([f":{f}:"for f in random.sample(food, 8)])}\n'
    message += f"<b>Mensa am Park\n{date}\n</b>"
    message += f'{"".join([f":{f}:"for f in random.sample(food, 8)])}\n\n'
    
    pizza = False
    smoothie = False
    fish = False 

    for meal in meals:
      name = meal.find("h4", {"class": "meals__name"}).text
      price = meal.find("p", {"class": "meals__price"}).text.replace("\n", "").replace(" ", "").replace("Preise:", "")
      
      if not pizza and "Pizza" in name:
        message += ":pizza::pizza::pizza::pizza::pizza:\n"
        pizza = True
      if not smoothie and "Smoothie" in name:
        message += f'{"".join([f":{fruit}:"for fruit in random.sample(fruits, 5)])}\n'
        smoothie = True
      if "Genießen Sie unsere frischen Smoothies!" not in name:
        message += f'{name}\n{price}\n\n'
      
    return message



  msg = emoji.emojize(menue_mensa_am_park())
  response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHANNEL_ID}&text={msg}&parse_mode=html")

except Exception as e:
  message = f"Feed Me Bot failed on reinlach machine.\nError Message:\n{str(e)}"
  response = requests.get(f"https://api.telegram.org/bot{MAINTAINER_TOKEN}/sendMessage?chat_id={MAINTAINER_CHATID}&text={message}&parse_mode=html")