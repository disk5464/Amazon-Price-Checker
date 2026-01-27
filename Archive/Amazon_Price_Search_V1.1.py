#Version 1.0: Initial Commit
#Version 1.1: Removed the sempai specific data filtering in place of regular json parsing. This will make it so that if the app needs to be restarted it can just use the existing files and not have to re scrap amazon
#################################################################
import serpapi, json, os
from pathlib import Path

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
        "asin": pr.get("asin"),
        "amazon_url": amazon_url,
        "item_name": specs.get("flavor"),
        "current_price": pr.get("extracted_price"),
        "precent_off": percentOff,
        "image": first_thumbnail,
        "source_file": path.name
    })

print(rows)
#################################################################

