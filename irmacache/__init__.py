import requests
import json
from time import sleep


__version__="0.2"

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
        response = requests.get(url,params)
        if response.ok:
            get_response = response.text
            self.cache.update({url + "?" + str(params):get_response})
            with open(self.filename,"w") as cache_file:
                json.dump(self.cache, cache_file)
            return get_response
        else:
            return f"403 Forbidden"

    def update_with_wait(self, url:str, params:dict, wait_time=180, number_tries=20):
        response = requests.get(url,params)
        counter = 1
        while not response.ok:
            sleep(wait_time)
            response = requests.get(url,params)
            counter += 1
            if counter > number_tries:
                break
        if response.ok:
            get_response = response.text
            self.cache.update({url + "?" + str(params):get_response})
            with open(self.filename,"w") as cache_file:
                json.dump(self.cache, cache_file)
            return get_response
        else:
            return f"Failed to get response"
        
    
    def get_and_wait(self, url:str, params:dict, wait_time=180, number_tries=20):
        key = url + '?' + str(params)
        if key not in self.cache.keys():
            get_response = self.update_with_wait(url, params, wait_time, number_tries)
        else:
            get_response = self.cache[key]
        return get_response
  
  
    def gw_json(self, url:str, params:dict, wait_time=180, number_tries=20):
        response = self.get_and_wait(url, params)
        try:
            return json.loads(response)
        except:
            print("could not return a json object")
            return response

    
    def get_json(self, url:str, params:dict):
        response = self.get(url, params)
        try:
            return json.loads(response)
        except:
            print("could not return a json object")
            return response
