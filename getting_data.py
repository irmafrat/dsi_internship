#WikiMedia project: Uses a URN to obtain JSON files of each objects. 
#The JSON files are being stored as cache. 
import csv
import requests
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

  
#Display of the data
def test():
    dict_list= data_csv()
    # print(len(dict_list))
    # input("enter any value:")
    base_save_dir = "/home/irma/Documents/dsi_currency_imgs/"
    total=0
    count_no_url = 0
    for row_dict in dict_list[:]: 
        # print(row_dict['Filename'])
        urn= clean_urn(row_dict['Filename'])
        metadata = search_library_cloud(urn)
        # print(metadata)
        total += 1
        try:
            url= metadata['items']['mods']['extension'][2]["DRSMetadata"]["fileDeliveryURL"]
            print(url)
        except:
            count_no_url += 1
            print("url not found")
            print(metadata['items']['mods'])
        # path_elements= url.split("/")[-1].split(":")
        # save_dir=base_save_dir + "/" + path_elements[0] + "/" + path_elements[1]
        # print(url.split("/")[-1].split(":"))
    print(f"no url on {count_no_url} of {total}")

test()

#Testing GitLab + GitHub!




