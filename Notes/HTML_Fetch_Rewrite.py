#Import the libaries
import requests
from bs4 import BeautifulSoup

#Make a list of the items we want to search
allASINs = ["B0DF1L929C", "B0GFC458B3", "B0FJVHTYK3", "B09YGL4BCM",
            "B08MWBFMX5", "B09YG6LN3W", "B0DQ6ZFD98", "B0BHKR7Z4L", "B08MW9LXK7"]

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

for ASIN in allASINs:
    URL = f"https://www.amazon.com/dp/{ASIN}"
    r = session.get(URL, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    # Quick block detection
    lower = r.text.lower()
    blocked = any(k in lower for k in ["robot check", "captcha", "/errors/validatecaptcha", "type the characters"])
    if blocked:
        print(ASIN, "BLOCKED (captcha/robot page)")
        print("##############################################################")
        continue

    # Main image
    main_img = soup.find("img", id="landingImage")
    thumbnail = main_img.get("src") if main_img else None

    # Title
    title_el = soup.find("span", id="productTitle")
    title = title_el.get_text(strip=True) if title_el else None

    # Your current flavor parsing can throw if there's no comma; make it safe:
    flavor = None
    if title and "," in title:
        parts = [p.strip() for p in title.split(",")]
        flavor = parts[1] if len(parts) > 1 else None

    # Price (try the apex buybox first, then core price display, then any a-offscreen)
    price_css_selectors = [
        "#apex_offerDisplay_desktop span.a-price span.a-offscreen",
        "#corePriceDisplay_desktop_feature_div span.aok-offscreen",
        "span.a-price span.a-offscreen",
    ]

    price = get_first_non_empty_text(soup, price_css_selectors).replace("$","")
    

    print("ASIN:", ASIN)
    print("Flavor:", flavor)
    print("Thumbnail:", thumbnail)
    print("Price:", price)
    print("##############################################################")
