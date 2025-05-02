import requests
import json

url = "https://2384.tainan.gov.tw/IMP/jsp/rwd_api/ajax_routeinfo.jsp?id=10451&lang=cht"
response = requests.get(url)
data = response.json()

print("路線名稱：", data["name"])

for stop in data["data"]:
    if f"{stop['stopSeq']:02d}" == "45" :
        print(f"{stop['stopSeq']:02d}. {stop['name']} - {stop['stopStatus']}")