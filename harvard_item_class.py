import requests
from time import sleep
import hashlib

class HarvardItem:
    max_retry=10
    permission = None # rights statement txt on progress/waiting OGC
    metadata_list=[
        "title","source","permission"
    ]
    
    def __init__(self, api_dict:dict):
        self.api_dict = api_dict
        self.urn = self.get_urn()
        self.url = self.get_url()
        self.deep_link = None
        self.title = self.get_title()
        self.media_binary = None
        self.embbed_urls = self.get_embbed_urls()
        self.source = self.get_source()

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
    
    def get_source(self):
        source = ""
        for key, value in self.embbed_urls.items():
            source += f"{key}: {value} - "
        return source[:-3]

    
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

    def wikimedia_csv(self):
        if self.permission is None:
            print("Permissions are required before generating CSV output.")
            return None
        csv_row=""
        for metadata in self.metadata_list:
            value = self.__getattribute__(metadata)
            if value is not None:
                # All values entered as strings
                # Used \" to identify quotes inside the string

                csv_row += '"' + value.replace('"', '""') + '",'
            else:
                csv_row += ','
        return csv_row[:-1]

    def wikimedia_source(self):
        if self.deep_link is None:
            self.deep_link = self.get_deep_link()
        return f"URL: {self.url} \nDeep Link: {self.deep_link}"

    def get_title(self):
        return self.api_dict['items']['mods']["titleInfo"]["title"].replace(", ", "_")
    
    def download_media(self):
        self.media_binary = self.get_content()
    
    def get_content(self):
        if self.deep_link is None:
            self.deep_link = self.get_deep_link()
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
    
    def set_permission(self, permission):
        self.permission = permission


    def get_embbed_urls(self):
        urls= {}
        #Add Hollis URL
        for related_item in self.api_dict['items']['mods']["relatedItem"]:
            if "@otherType" in related_item.keys():
                if related_item["@otherType"].lower() ==  "HOLLIS Images record".lower():
                    hollis_images = related_item["location"]["url"]
                    urls.update({"Harvard Hollis Images": hollis_images})
        #Adds Harvard Digital Collection and CURIOSity
        for location in self.api_dict["items"]["mods"]["location"]:
            if "url" in location.keys():
                for url in location["url"]:
                    if type(url) is dict:
                        if "@displayLabel" in url.keys():
                            urls.update({url['@displayLabel']: url['#text']})
        return urls

    def filename(self):
       return f"{self.urn.replace(':','_')}_{self.title}"


class CurrencyItem(HarvardItem):
    institution = "Q49126" # HBS. WikiData institution item identifier 
    department = "Q42377658" # Baker. WikiData institution item identifier 
    metadata_list_currency=[
        "author","description","date","medium","dimensions","institution",
        "department","notes","accession_number"]
    def __init__(self,api_dict:dict, csv_dict:dict):
        super().__init__(api_dict)
        self.csv_dict = csv_dict
        self.author = self.get_author() # data is in the CSV
        self.description = self.get_description()
        self.dimensions = self.get_dimensions()
        self.medium = self.get_medium()
        self.date = self.get_date()
        self.inscriptions = self.get_inscriptions()
        self.notes = self.get_notes()
        self.accession_number = self.get_accession_number()
        self.other_versions = self.get_other_versions() #Hollis URL (Verso and Recto images on the same record)

    def wikimedia_csv(self):
        csv_row = super().wikimedia_csv() + ","
        for metadata in self.metadata_list_currency:
            value = self.__getattribute__(metadata)
            if value is not None:
                print(value)
                if metadata == "date" and type(value) is dict:
                    value = value["date1"]
                csv_row += '"' + value.replace('"', '""') + '",'
            else:
                csv_row += ','
        return csv_row[:-1]


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
    
    def get_author(self):
        return self.csv_dict["Creator[33420]"]

    def get_description(self):
        try:
            return self.api_dict['items']['mods']["abstract"]
        except:
            return None

    def get_dimensions(self):
        try:
            return self.api_dict['items']['mods']["physicalDescription"]["extent"]
        except:
            # TODO Get from CSV
            return None

    def get_medium(self):
        # api_medium = self.api_dict['items']['mods']["note"][0] #Add to get_notes
        csv_medium = self.csv_dict["Materials/Techniques[33429]"]
        return f"{csv_medium}"

    def get_date(self):
        start = None
        end = None
        date_str = None
        if "originInfo" not in self.api_dict['items']['mods'].keys():
            return self.get_date_csv()
        if "dateCreated" not in self.api_dict['items']['mods']["originInfo"].keys():
            return self.get_date_csv()
        for date in self.api_dict['items']['mods']["originInfo"]["dateCreated"]: 
            if type(date) is dict:
                if "@point" in date.keys():
                    if date["@point"] == "start":
                        start = date["#text"]
                    elif date["@point"] == "end":
                        end = date["#text"]
            elif type(date) is str:
                date_str = date
        if start == end and start is not None:
            return start
        elif date_str[:4] == "ca. ":
            return {"date1": date_str.split(" ")[-1], "precision1": "decade"}
        else:
            if start is not None:
                return start
            if end is not None:
                return end
            return date_str

    def get_date_csv(sefl):
        # TODO
        return None

    def get_inscriptions(self):
        try:
            return self.api_dict['items']['mods']["note"][2]
        except:
            return None

    def get_notes(self):
        for extension in self.api_dict["items"]["mods"]["extension"]:
            if "DRSMetadata" in extension.keys():
                citation = extension["DRSMetadata"]["metsLabel"]
                return f"citation: {citation}"
        print("No citation found.")
        return None

    def get_accession_number(self):
        attribution = self.api_dict["items"]["mods"]["recordInfo"]["recordIdentifier"]["@source"]
        record_info = self.api_dict["items"]["mods"]["recordInfo"]["recordIdentifier"]["#text"]
        return f"{attribution} {record_info}"

    def get_other_versions(self):
        for related_item in self.api_dict['items']['mods']["relatedItem"]:
            if "@otherType" in related_item.keys():
                if related_item["@otherType"].lower() ==  "HOLLIS Images record".lower():
                    hollis_images = related_item["location"]["url"]
                    return f"Harvard Hollis Images: {hollis_images}"
        return None

    