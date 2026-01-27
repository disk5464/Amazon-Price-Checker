import serpapi, json, os

#################################################################
#Set an array of all of the items we want to search. 
allASINs = ['B0DF1L929C']

#################################################################
#Define a function that will figure out where the script is running. This is used to get the folder path for the output json
def get_base_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()

#Define the class that will create the objects for each flavor
class Single_Amazon_Item:
  def __init__(self, image, name, price, discount):
    self.image = image
    self.name = name
    self.price = price
    self.discount = precentOff

#Define the function that caculates the precent off MSRP
def get_percentage_decrease(price, msrp):
    return ((price - msrp) / msrp) * 100

#################################################################
#This section will get the scirpt's directory, make a FDQN path out of it, then if the json out put directory dosen't exist make it. 
base_dir = get_base_dir()
output_dir = os.path.join(base_dir, "current_ASINs")
os.makedirs(output_dir, exist_ok=True)

#################################################################
for item in allASINs:
    #Print the item, then run the search and save the results to ItemOut
    params = {"engine": "amazon_product","asin": item,"api_key": ""}
    serpapiObject = serpapi.search(params)
    
    #Convert the serpapi object into a normal dictionary. Then convert to json and save it to a file.
    ItemOutDict = serpapiObject.as_dict()
    output_path = os.path.join(output_dir, f"{item}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ItemOutDict, f, indent=2, ensure_ascii=False)
    
    #Check if the current price is lower than the MSRP ($30.00)
    if( (ItemOutDict["product_results"]["extracted_price"]) < 29.99):
        #Set a variable for the MSRP then use it along with the current price to figure out what precent off it is. Finally set a variable for the fact that it is on sale
        msrp = 29.99
        price = ItemOutDict["product_results"]["extracted_price"]
        precentOff = round(get_percentage_decrease(price, msrp)),"%"
    else:
        precentOff = "Not on Sale"
    
    #Create the basic item object. This uses Single_Amazon_Item class to create the object. It has a name, price, and discount property
    single_item = Single_Amazon_Item(ItemOutDict["product_results"]["thumbnails"][0], ItemOutDict["item_specifications"]["flavor"], ItemOutDict["product_results"]["extracted_price"], precentOff)

    #Print the results
    print(single_item.name, single_item.price, single_item.discount)
