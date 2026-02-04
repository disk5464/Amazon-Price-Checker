#Version 1.0: Initial Commit
#Version 1.1: Removed the sempai specific data filtering in place of regular json parsing. This will make it so that if the app needs to be restarted it can just use the existing files and not have to re scrap amazon
#################################################################
import os, requests, time, bs4
import streamlit as st
from pathlib import Path
from bs4 import BeautifulSoup

#################################################################
#Set an array of all of the items we want to search. Then set an empty array for the output items
allASINs = ["B0DF1L929C", "B0GFC458B3", "B0FJVHTYK3", "B09YGL4BCM", "B08MWBFMX5", "B09YG6LN3W", "B0DQ6ZFD98", "B0BHKR7Z4L", "B08MW9LXK7"]
#allASINs = ['B0DF1L929C']

rows = []
#################################################################
#Define the function that caculates the precent off MSRP
def get_percentage_decrease(price, msrp):
    return ((price - msrp) / msrp) * 100

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

#################################################################
#Create a new session variable and add in some headers so that the requests look more like a browser made them
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
})

#################################################################
#This for loop will scrape amazon for each product page and export it to a json file
for ASIN in allASINs:
    #Reset the blocked variable. This is so that the script will retry untill it becomes unblocked
    currentlyblocked = True

    #While the search was blocked
    while currentlyblocked == True :
        amazon_url = f"https://www.amazon.com/dp/{ASIN}"
        r = session.get(amazon_url, timeout=20)
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

            #################################################################
            #Scrap the main item image and save it to a variable
            main_img = soup.find("img", id="landingImage")
            thumbnail = main_img.get("src") if main_img else None

            #################################################################
            #Get the item's main title and save it to a variable. This variable has a bunch of junk in it and needs to be cleaned "GHOST Energy Drink - 12-Pack, Welch's Grape, 16oz Cans Blah blah blah"
            title_el = soup.find("span", id="productTitle")
            title = title_el.get_text(strip=True) if title_el else None

            #Take the title, split it on the commas, then select the second item in that list, which is just the flavor (Welch's Grape). Save that to an output variable
            flavor = None
            if title and "," in title:
                parts = [p.strip() for p in title.split(",")]
                flavor = parts[1] if len(parts) > 1 else None
            
            #################################################################
            #There are 3 different places where the price can spawn in the HTML depending on how the page loads. Set an array of each localtion.
            price_css_selectors = [
                "#apex_offerDisplay_desktop span.a-price span.a-offscreen",
                "#corePriceDisplay_desktop_feature_div span.aok-offscreen",
                "span.a-price span.a-offscreen",
            ]

            #Feed that array into the function that finds out if the price is present. Return that value, remove the dollar sign, save it to an output variable
            currentPrice = float(get_first_non_empty_text(soup, price_css_selectors).replace("$",""))

            #Figure out if the item is on sale or not
            if currentPrice is not None and currentPrice < 29.99:
                #Set a variable for the MSRP then use it along with the current price to figure out what precent off it is. Finally set a variable for the fact that it is on sale
                msrp = 29.99
                percentOff = f"{round(get_percentage_decrease(currentPrice, msrp))} %"

            else:
                percentOff = "Not on Sale"

            #################################################################
            #Create the "table" with each row being a differen json file and its extracted data
            rows.append({
                #"asin": pr.get("asin"),
                "image": thumbnail,
                "item_name": flavor,
                "current_price": currentPrice,
                "precent_off": percentOff,
                "URL": amazon_url
            })

#################################################################
#This section will build the streamlit web page. First start by setting the CSS of each section
st.markdown("""
<style>
/* This is the main control for the hights of both the header and rows */
:root {
  --row-h: 180px;
  --hdr-h: 60px;
}

/* This sets the header center alignment and font size */
.header-cell {
  height: var(--hdr-h);
  display: flex;
  align-items: center;      /* vertical center */
  font-size: 2.0rem;
  font-weight: 700;
}

/* This sets the header horzontral alignment, font size, and centers the text within */
.header-cell-center {
  height: var(--hdr-h);
  display: flex;
  align-items: center;
  justify-content: center;  /* horizontal + vertical center */
  font-size: 2.0rem;
  font-weight: 700;
}

/* This sets the row center alignment and font size */
.cell {
  height: var(--row-h);
  display: flex;
  align-items: center;      /* vertical center */
  font-size: 2.05rem;
  font-weight:600;
}

/* This sets the row horzontral alignment, font size, and centers the text within */
.cell-center {  
  height: var(--row-h);
  display: flex;
  align-items: center;      /* vertical center */
  justify-content: center;  /* horizontal center */
  font-size: 2.05rem;
  font-weight:600;
}
</style>
""", unsafe_allow_html=True)

#################################################################
#This section will build the streamlit webpage. First set the title of the browser tab and create a header on the top of the page
st.set_page_config(page_title="Price Tracker", layout="wide")
st.markdown("<h1 style='text-align:center; margin-bottom: 0;'>Amazon Energy Drink Price Tracker</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; margin-bottom: 0;'>This table will show you the current prices of Ghost energy on Amazon</h1>", unsafe_allow_html=True)

#Since we are not using an actual table or a data frame we need to build the table row by row. This sets the header row. First declair the header variables
headerRow1, headerRow2, headerRow3, headerRow4 = st.columns([1, 1, 1, 1])

#Next for each header, set the text and set the style type we are using
with headerRow1:
    st.markdown("<div class='header-cell'>Product Image</div>", unsafe_allow_html=True)

with headerRow2:
    st.markdown("<div class='header-cell'>Name</div>", unsafe_allow_html=True)

with headerRow3:
    st.markdown("<div class='header-cell-center'>Current Price</div>", unsafe_allow_html=True)

with headerRow4:
    st.markdown("<div class='header-cell-center'>Discount</div>", unsafe_allow_html=True)
st.divider()

#For each product (each row of json), 
for r in rows:
    #Declair variables for each column 
    c1, c2, c3, c4 = st.columns(4)

    #For the image column, if the input data ("image": first_thumbnail) and the URL ("URL": amazon_url) is populated the image and make it a cliclable link to the amazon page. If not just show a dash
    with c1:
        #Set the image and url to local variables
        img = r.get("image")
        url = r.get("URL")  # note: your key is "URL" (uppercase)
        
        #If the image and url both exist
        if img and url:
            #Set the image to have the url imbeaded in it. This makes it clickable.
            st.markdown(
                f"""
                <a href="{url}" target="_blank" rel="noopener noreferrer">
                    <img src="{img}" style="width:200px; height:auto; border-radius:8px;" />
                </a>
                """,
                unsafe_allow_html=True
            )
        elif img:
            st.image(img, width=200)
        else:
            st.write("—")

    #For the item name column, pass in the item name, if its missing just display unknown
    with c2:
        #Get the item name and product URL (Same as C1) and set them to variables
        name = r.get("item_name", "Unknown")
        url = r.get("URL")
        
        #if they both exist make the name a clickable link, if the url is missing just display the name
        if url:
            st.markdown(f"<div class='cell'><a href='{url}' target='_blank'>{name}</a></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='cell'>{name}</div>", unsafe_allow_html=True)

    #For the current price column, check the price, if it is on sale make it green, MSRP make it white, Overpriced, make it red
    with c3:
        #Take the price from the json and make it a normal variable
        price = r.get("current_price")
        
        #Check the price, then color accordingly
        if price is not None and price < 29.99:
            price_html = f"<div class='cell-center'; span style='color:#22c55e'>${price:.2f}</span></div>"
        elif price is not None:
            price_html = f"<div class='cell-center'; span style='color:#FF0000'>${price:.2f}</span></div>"
        else:
            price_html = "<span style='color:#FFFFFF'>Out of Stock</span>"

        #Display the price on the table
        st.markdown(f"<div class='cell-center'>{price_html}</div>", unsafe_allow_html=True)

    #For the discount column, display the precent off
    with c4:
        st.markdown(f"<div class='cell-center'>{r.get('precent_off', 'N/A')}</div>", unsafe_allow_html=True)

    #Add the line between each row
    st.markdown("<hr style='margin: 6px 0;'>", unsafe_allow_html=True)
