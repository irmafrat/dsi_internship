#WikiMedia project: Clean, save and map digital object URN
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


#Search in API using the URN and returning a json file
def search_library_cloud(urn: str):
    base_url= "https://api.lib.harvard.edu/v2/items.json"
    params = {'urn': urn}
    # response = requests.get(base_url,params).json()
    response= cache.get_json(base_url,params)
    return response


  
#Display of the data
def test():
    dict_list= data_csv()
    # print(len(dict_list))
    # input("enter any value:")
    for row_dict in dict_list: 
        # print(row_dict['Filename'])
        urn= clean_urn(row_dict['Filename'])
        print(search_library_cloud(urn))




        

test()



# def libcloud_search(urn='urn-3:FHCL:1155043'):

