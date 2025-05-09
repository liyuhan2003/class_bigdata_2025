import requests
import json

url = "https://od.moi.gov.tw/api/v1/rest/datastore/A01010000C-001309-001/?limit=200000"
response = requests.get(url)
data = response.json()
data = data["result"]["records"]

for item in data:
    print(f'{item["ACCYMD"]} {item["PLACE"]} {item["CARTYPE"]}')
