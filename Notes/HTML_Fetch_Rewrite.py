#Import the libaries
import requests, time
from bs4 import BeautifulSoup

#Make a list of the items we want to search
#allASINs = ["B0DF1L929C", "B0GFC458B3", "B0FJVHTYK3", "B09YGL4BCM","B08MWBFMX5", "B09YG6LN3W", "B0DQ6ZFD98", "B0BHKR7Z4L", "B08MW9LXK7"]
allASINs = ["B0DQ6ZFD98"]
#Create a new session variable and add in some headers so that the requests look more like a browser made them
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
})

#Define a function that takes in the soup object and a list of possible HTML elements. Check each one to see if they have any text in them. Return any found text
def get_first_non_empty_text(html_soup, css_selectors):
    for selector in css_selectors:
        #Select just the html from the entire element
        matched_element = html_soup.select_one(selector)

        #If it's empty continue to the next HTML element
        if matched_element is None:
            continue

        extracted_text = matched_element.get_text(strip=True)

        if extracted_text:
            return extracted_text

    return None

#For each item we are going to search
for ASIN in allASINs:
    #Reset the blocked variable. This is so that the script will retry untill it becomes unblocked
    currentlyblocked = True
    
    #While the search was blocked
    while currentlyblocked == True :
        URL = f"https://www.amazon.com/dp/{ASIN}"
        r = session.get(URL, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")

        # Quick block detection
        lower = r.text.lower()
        blocked = any(k in lower for k in ["robot check", "captcha", "/errors/validatecaptcha", "type the characters"])

        #If the script is currently blocked wait 2 seconds then rerun that item's search
        if blocked:
            print(ASIN, "BLOCKED (captcha/robot page)")
            print("##############################################################")
            currentlyblocked = True
            time.sleep(2)
            continue
        else: 
            #Set the block variable to False so we will move onto the next item after this pass since we are not blocked
            currentlyblocked = False

            #Scrap the main item image and save it to a variable
            main_img = soup.find("img", id="landingImage")
            thumbnail = main_img.get("src") if main_img else None

            #Get the item's main title and save it to a variable. This variable has a bunch of junk in it and needs to be cleaned "GHOST Energy Drink - 12-Pack, Welch's Grape, 16oz Cans Blah blah blah"
            title_el = soup.find("span", id="productTitle")
            title = title_el.get_text(strip=True) if title_el else None

            #Take the title, split it on the commas, then select the second item in that list, which is just the flavor (Welch's Grape). Save that to an output variable
            flavor = None
            if title and "," in title:
                parts = [p.strip() for p in title.split(",")]
                flavor = parts[1] if len(parts) > 1 else None

            #There are 3 different places where the price can spawn in the HTML depending on how the page loads. Set an array of each localtion.
            price_css_selectors = [
                "#apex_offerDisplay_desktop span.a-price span.a-offscreen",
                "#corePriceDisplay_desktop_feature_div span.aok-offscreen",
                "span.a-price span.a-offscreen",
            ]

            #Feed that array into the function that finds out if the price is present. Return that value, remove the dollar sign, save it to an output variable
            price = get_first_non_empty_text(soup, price_css_selectors).replace("$","")

            print("ASIN:", ASIN)
            print("Flavor:", flavor)
            print("Thumbnail:", thumbnail)
            print("Price:", price)
            print("##############################################################")





#TO DO: 
# Need to figure out how to handle when an item is sold out
# Need to add something to the beginning while the data is being pulled. 
# Need to add a print() for when an item is found (Makes it easier to check that it works)
#
#