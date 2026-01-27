#Version 1.0: Initial Commit
#Version 1.1: Removed the sempai specific data filtering in place of regular json parsing. This will make it so that if the app needs to be restarted it can just use the existing files and not have to re scrap amazon
#################################################################
import serpapi, json, os
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

#################################################################
#Set an array of all of the items we want to search. 
#asin_codes = ["B0DF1L929C", "B0GFC458B3", "B0FJVHTYK3", "B09YGL4BCM", "B08MWBFMX5", "B09YG6LN3W", "B0DQ6ZFD98", "B0BHKR7Z4L", "B08MW9LXK7"]
allASINs = ['B0DF1L929C']

#################################################################
#Define a function that will figure out where the script is running. This is used to get the folder path for the output json
def get_base_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()

#Define the function that caculates the precent off MSRP
def get_percentage_decrease(price, msrp):
    return ((price - msrp) / msrp) * 100

#################################################################
#This section will get the scirpt's directory, make a FDQN path out of it, then if the json out put directory dosen't exist make it. 
base_dir = get_base_dir()
output_dir = os.path.join(base_dir, "current_ASINs")
os.makedirs(output_dir, exist_ok=True)

#################################################################
#This for loop will scrape amazon for each product page and export it to a json file
for item in allASINs:
    #Print the item, then run the search and save the results to ItemOut
    params = {"engine": "amazon_product","asin": item,"api_key": "6ff7d4ee7fc220f3cb61b8b924b7fec16e93352dacf2f187198d857e7950492f"}
    serpapiObject = serpapi.search(params)
    
    #Convert the serpapi object into a normal dictionary. Then convert to json and save it to a file.
    ItemOutDict = serpapiObject.as_dict()
    output_path = os.path.join(output_dir, f"{item}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ItemOutDict, f, indent=2, ensure_ascii=False)
        
#################################################################
#This section will import the json files, parse them for the info we want, then export it to the rows array. Which we will use for the grid later.

#First get the the path that the script is running at to get all of the json files in the output directory. Then create the output array
paths = list(Path(output_dir).glob("*.json"))
rows = []

for path in paths:
    #Load in the json file
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    #################################################################
    #set vairables for the item_specs and product_results sections of the json
    specs = data.get("item_specifications", {})
    pr = data.get("product_results", {})
    
    #Use the products resutls variable from about, select the thumbnails section within, then select just the first link. If there are no images set it to none
    thumbnails = pr.get("thumbnails", [])
    first_thumbnail = thumbnails[0] if thumbnails else None
    
    #Figure out the precent off. Check if the current price is lower than the MSRP ($30.00)
    currentPrice = pr.get("extracted_price")
    
    #################################################################
    #Figure out if the item is on sale or not
    if currentPrice is not None and currentPrice < 29.99:
        #Set a variable for the MSRP then use it along with the current price to figure out what precent off it is. Finally set a variable for the fact that it is on sale
        msrp = 29.99
        percentOff = f"{round(get_percentage_decrease(currentPrice, msrp))} %"

    else:
        percentOff = "Not on Sale"

    #################################################################
    #Set a variable for the URL to the item's amazon page
    amazon_url = f"https://www.amazon.com/dp/{asin}/" if asin else None
    
    #################################################################
    #Create the "table" with each row being a differen json file and its extracted data
    rows.append({
        #"asin": pr.get("asin"),
        "image": first_thumbnail,
        "item_name": specs.get("flavor"),
        "current_price": pr.get("extracted_price"),
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
