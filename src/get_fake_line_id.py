import requests

url="https://2384.tainan.gov.tw/IMP/jsp/rwd_api/ajax_routeinfo_pathattr.jsp?id=1101&Lang=cht"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()  # 直接解析 JSON

    stops = data.get("data", [])  # 提取站牌資料清單

    for stop in stops:
        seq = stop.get("seq", "未知")
        stop_info = stop.get("stopInfo", "無資料")
        print(f"第 {seq} 站 - 狀態：{stop_info}")

else:
    print("Request failed. Status code:", response.status_code)

    