#WikiMedia project: Uses a URN to obtain JSON files of each objects. 
#The JSON files are being stored as cache. 
import csv
import requests
import os.path
import hashlib
from irmacache import Cache


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
def image_deep_url(url:str):
    response= requests.get(url)
    if response.ok:
        image_binary = response.content
        # if response.status_code == 200:
        #     deep_url = url
        # else:
        #     deep_url = response.url
        deep_url = response.url
        return image_binary, deep_url
    return None, None


# >>> 
# >>> 
# '2a53375ff139d9837e93a38a279d63e5'


#Saves Image 
def save_image(
            image_binary: bin, urn: str, url: str, deep_url: str,
            csv_file="image_data.csv", image_save_dir = "/home/irma/Documents/dsi_currency_imgs/"
        ):
    image_filename = urn.replace(":", "_") + ".jpeg"
    image_absolute_filename = image_save_dir + image_filename
    with open(image_absolute_filename, "wb") as handler:
        handler.write(image_binary)
    
    md5sum = hashlib.md5(image_binary).hexdigest()
    
    with open(csv_file,"a") as handler:
        row = f"{urn},{url},{deep_url},{image_filename},{md5sum}\n"
        print(row)
        handler.write(row)

def main():
    dict_list= data_csv()
    # print(len(dict_list))
    # input("enter any value:")
    base_save_dir = "/home/irma/Documents/dsi_currency_imgs/"

    if not os.path.isdir(base_save_dir):
        os.makedirs(base_save_dir)

    total=0
    count_no_url = 0
    image_filename_metadata = "image_filename.csv"

    # Initialize metadata file
    with open(image_filename_metadata,"w") as handler:
        handler.write(f"urn,url,deep_url,image_filename,md5sum\n")
    
    # Download Images
    for row_dict in dict_list[:]: 
        total += 1
        print(total)
        urn= clean_urn(row_dict['Filename'])
        url=finding_url(urn)
        if url is not None:
            image_binary, deep_url = image_deep_url(url)
            save_image(image_binary, urn, url=url, deep_url=deep_url, csv_file=image_filename_metadata, image_save_dir=base_save_dir)
        else:
            count_no_url += 1
    print(f"no url on {count_no_url} of {total}")


if __name__ == "__main__":
    main()


