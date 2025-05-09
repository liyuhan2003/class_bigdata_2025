import requests
import json

url = "https://od.moi.gov.tw/api/v1/rest/datastore/A01010000C-001309-001/?limit=200000"
response = requests.get(url)
data = response.json()
data = data["result"]["records"]

COUNT = 0
for item in data:
    if "114年03月10日" in item["ACCYMD"]:
        COUNT += 1
        print(f'{item["ACCYMD"]} {item["PLACE"]} {item["CARTYPE"]}')
print(COUNT)
