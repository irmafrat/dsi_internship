#WikiMedia project: Scrape images from Harvard Digital Collections page. 
# Clean, save and map digital object URN.
import requests
import os
from bs4 import BeautifulSoup
import json
import urllib


# with open('currency_cache.json') as data_file:
#     data = json.load(data_file)


# url= "https://nrs.harvard.edu/urn-"
# #the url above changes to this page https://ids.lib.harvard.edu/ids/view/


# #Uses the "currency_cache.json" to access image link and return an jpeg image. 
# def get_images():
#     for dictionary in data: 







