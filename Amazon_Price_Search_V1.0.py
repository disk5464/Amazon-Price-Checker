import serpapi, json

#################################################################
#Set an array of all of the items we want to search. 
allASINs = ['B0DF1L929C']

#################################################################
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
for item in allASINs:
    #Print the item, then run the search and save the results to ItemOut
    params = {"engine": "amazon_product","asin": item,"api_key": "6ff7d4ee7fc220f3cb61b8b924b7fec16e93352dacf2f187198d857e7950492f"}
    serpapiObject = serpapi.search(params)
    
    #Convert the serpapi object into a normal dictionary. Then convert to json. This makes it so it can be copy pasted without a bunch of formating issues
    ItemOutDict = serpapiObject.as_dict()
    
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
