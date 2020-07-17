#WikiMedia project: Uses a URN to obtain JSON files of each objects. 
#The JSON files are being stored as cache. 
import csv
import requests
import os.path
import hashlib
from time import sleep
from irmacache import Cache
import harvard_item_class as hic 



cache= Cache(filename='currency_cache.json')


#Returns a list of dictionaries
def data_csv(filename="American Currency collection_money-JSTOR.csv"):
    out=[]
    with open(filename,'r') as csv_file: 
        csv_reader = csv.DictReader(csv_file)
        for row_dict in csv_reader:
            out.append(row_dict.copy())
    return out



#Returns the urn according to the LibraryCloudAPI
# drs:urn-3:HBS.Baker.AC:1142292
# urn-3:HBS.Baker.AC:1142292
def clean_urn(dirty_urn): 
    return dirty_urn[4:] 


#Search in API using the URN and returning a dictionary. The response will be saved on a cache file. 
def search_library_cloud(urn: str):
    base_url= "https://api.lib.harvard.edu/v2/items.json"
    params = {'urn': urn}
    # response = requests.get(base_url,params).json()
    response= cache.gw_json(base_url,params,wait_time=15,number_tries=2)
    return response


 
#Test if there is a url on two diferent locations of the urn dictionary. Returns the URL.
def finding_url(urn:str):
    # TO DO RETURN CLASS INSTEAD OF URL. CREATE A CLASS TO GET TITLE, YEAR, AND METADATA REQUIRED BY THE WIKIMEDIA TEMPLATE. 
    metadata = search_library_cloud(urn)
    # print(metadata)
    try:
        url = metadata['items']['mods']["relatedItem"][2]["location"]['url'][0]["#text"]
        # print(url)
    except:
        try:
            url= metadata['items']['mods']['extension'][2]["DRSMetadata"]["fileDeliveryURL"]
        except:
            print("url not found")
            # print(metadata['items']['mods'])
            print(metadata)
            return None
    return url

#Download and get deep url. Returns a tuple with two elements.
def image_deep_url(url:str, image_filename: str, max_retry=60):
    # TO DO EXTRACT BINARY FROM FILE AND DEEP URL USING HEAD INSTEAD OF GET 
    # (IF FILE EXISTS NEW METHOD ELSE DO OLD VERSION)
    response= requests.get(url)
    total_tries= 0
    while not response.ok:
        total_tries +=1
        print(f"Retry #{total_tries}")
        sleep(30)
        response= requests.get(url)
        if total_tries > max_retry:
            break

    if response.ok:
        image_binary = response.content
        # if response.status_code == 200:
        #     deep_url = url
        # else:
        #     deep_url = response.url
        deep_url = response.url
        return image_binary, deep_url
    return None, None



#Saves Image 
def save_image(
            image_binary: bin, urn: str, url: str, deep_url: str, image_filename:str,
            csv_file="image_data.csv"
        ):
    with open(image_filename, "wb") as handler:
        handler.write(image_binary)
    
    sha1 = hashlib.sha1(image_binary).hexdigest()
    
    with open(csv_file,"a") as handler: # updates (appends to the end of file)
        row = f"{urn},{url},{deep_url},{image_filename.split('/')[-1]},{sha1}\n"
        print(row)
        handler.write(row)

def main():

    base_save_dir = "/home/irma/Documents/dsi_currency_imgs/"
    if not os.path.isdir(base_save_dir):
        os.makedirs(base_save_dir)

    image_filename_metadata = "wikimedia_bash_upload.csv"

    # Initialize metadata file
    metadata_column_list=["title","source","permission","author","description","date","medium","dimensions","institution",
        "department","notes","accession number"]
    handler = open(image_filename_metadata,"w")
    for metadata in metadata_column_list[:-1]:
        handler.write(metadata + ",")
    handler.write(metadata_column_list[-1] + "\n")
    
    dict_list= data_csv()

    total=0
    count_no_url = 0
    
    
    # Download Images
    skip = 0
    total += skip
    for csv_dict in dict_list[skip:]: 
        total += 1
        print(total)
        urn= clean_urn(csv_dict['Filename'])
        api_dict = search_library_cloud(urn)
        item = hic.CurrencyItem(api_dict,csv_dict)
        item.permission="Rights Statements in evaluation, waiting for OGC. No permission granted."
        print(item.filename())
        csv_row = item.wikimedia_csv()
        print(csv_row)
        handler.write(csv_row + "\n")
    handler.close()




    #     image_title = "" # To do
    #     image_filename = image_title + "_" + urn.replace(":", "_") + ".jpeg"
    #     image_absolute_filename = base_save_dir + image_filename
    #     url=finding_url(urn)
    #     if url is not None:
    #         image_binary, deep_url = image_deep_url(url, image_absolute_filename)
    #         save_image(image_binary, urn, url=url, deep_url=deep_url, csv_file=image_filename_metadata, image_filename=image_absolute_filename)
    #     else:
    #         count_no_url += 1
    # print(f"no url on {count_no_url} of {total}")


if __name__ == "__main__":
    main()


