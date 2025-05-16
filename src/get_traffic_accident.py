import requests
from datetime import datetime

def convert_minguo_to_gregorian(minguo_datetime_str):
    try:
        parts = minguo_datetime_str.split("年")
        year = int(parts[0]) + 1911
        rest = parts[1]
        full_datetime_str = f"{year}年{rest}"
        return datetime.strptime(full_datetime_str, "%Y年%m月%d日 %H時%M分%S秒")
    except Exception:
        return None

url = "https://od.moi.gov.tw/api/v1/rest/datastore/A01010000C-001309-001"
response = requests.get(url)
data = response.json()
data = data["result"]["records"]

count = 0  # 計數器

for item in data:
    accymd = item["ACCYMD"]

    # 跳過表頭
    if accymd == "發生時間":
        continue

    dt = convert_minguo_to_gregorian(accymd)
    if dt:
        formatted_time = dt.strftime("%Y年%m月%d日 %H點%M分%S秒")
        place = item["PLACE"]
        cartype = item["CARTYPE"]
        print(f"{formatted_time} {place} {cartype}")
        count += 1
    else:
        print(f"時間格式錯誤：{accymd}")

# 印出總筆數
print(f"\n總共有 {count} 筆有效資料")
