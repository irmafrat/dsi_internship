import requests
from time import sleep
import hashlib

class HarvardItem:
    max_retry=10

    def __init__(self, api_dict:dict):
        self.api_dict = api_dict
        self.urn = self.get_urn()
        self.url = self.get_url()
        self.deep_link = self.get_deep_link()
        self.title = self.get_title()
        self.filename = self.construct_filename() # TODO
        self.media_binary = None

        # TODO WORK WITH FILENAME AND SHA1

    def get_urn(self):
        return self.api_dict["pagination"]["query"][4:]
    
    def get_url(self):
        try:
            url = self.api_dict['items']['mods']["relatedItem"][2]["location"]['url'][0]["#text"]
        except:
            try:
                url= self.api_dict['items']['mods']['extension'][2]["DRSMetadata"]["fileDeliveryURL"]
            except:
                return f"No URL found"
        return url
    
    def get_deep_link(self):
        if self.url == "No URL found":
            return "Required URL to get deep link."
        response= requests.head(self.url)
        total_tries= 0
        while not response.ok:
            total_tries +=1
            print(f"Retry #{total_tries}")
            sleep(30)
            response= requests.head(self.url)
            if total_tries > self.max_retry:
                break

        if response.ok:
           
            deep_url = response.headers['Location']
            return deep_url
        return deep_url

    def wikimedia_source(self):
        return f"URL: {self.url} \nDeep Link: {self.deep_link}"

    def get_title(self):
        return self.api_dict['items']['mods']["titleInfo"]["title"].replace(", ", "_")
    
    def download_media(self):
        self.media_binary = self.get_content()
    
    def get_content(self):
        if self.deep_link == "Required URL to get deep link.":
            print("Required deep link to download media binary.")
            return None
        response= requests.get(self.deep_link)
        total_tries= 0
        while not response.ok:
            total_tries +=1
            print(f"Retry #{total_tries}")
            sleep(30)
            response= requests.get(self.deep_link)
            if total_tries > self.max_retry:
                break

        if response.ok:
            media_binary = response.content
            return media_binary
        else: 
            print("Could not download media")
            return None




class CurrencyItem(HarvardItem):
    def __init__(self,api_dict:dict, csv_dict:dict):
        super().__init__(api_dict)
        self.csv_dict = csv_dict
        self.author = get_author() # data is in the CSV
        self.description = get_description()
        self.dimensions = get_dimensions()
        self.medium = get_medium()
        self.institution = get_institution()
        self.date = get_date()
        self.inscriptions = get_inscriptions()
        self.notes = get_notes()
        self.accession_num = get_accession_num()
        self.permission = get_permission # rights statement txt on progress/waiting OGC
        self.other_versions = get_other_versions() #Hollis URL (Verso and Recto images on the same record)
    

    def get_title(self):
        title = super().get_title()
        verso_recto = self.get_verso_recto()
        if verso_recto is None:
            return title
        else:
            return f"{verso_recto}_{title}"
    
    def get_verso_recto(self):
        for related_item in self.api_dict['items']['mods']["relatedItem"]:
            if "@type" in related_item.keys():
                if related_item["@type"] == "constituent":
                    return related_item["titleInfo"]["title"]
        return None
    