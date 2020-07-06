import requests
import json


class Cache:
    def __init__(self, filename="irma_cache.json"):
        self.filename= filename
        self.cache = self.load_cache()


    def load_cache(self):
        try:
            with open(self.filename, 'r') as handler:
                cache = json.load(handler)

        except FileNotFoundError:
            cache = {}
        return cache


    def get(self, url:str, params:dict):
        key = url + '?' + str(params)
        if key not in self.cache.keys():
            get_response = self.update(url, params)
        else:
            get_response = self.cache[key]
        return get_response

    def delete(self, url:str, params:dict):
        self.cache.pop(url + "?" + str(params))
        with open(self.filename,"w") as cache_file:
            json.dump(self.cache, cache_file)

    def update(self, url:str, params:dict):
        get_response = requests.get(url,params).text
        self.cache.update({url + "?" + str(params):get_response})
        with open(self.filename,"w") as cache_file:
            json.dump(self.cache, cache_file)
        return get_response
    
    def get_json(self, url:str, params:dict):
        response = self.get(url, params)
        try:
            return json.loads(response)
        except:
            print("could not return a json object")
            return response
