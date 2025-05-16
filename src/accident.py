import requests
import json
import re, datetime
import psycopg2

def parse_line(line):
    try:
        date_match = re.match(r"^(\d{3})年(\d{2})月(\d{2})日 (\d{2})時(\d{2})分(\d{2})秒", line)
        if not date_match:
            raise ValueError("無法解析日期時間格式")

        year = int(date_match.group(1)) + 1911
        month = int(date_match.group(2))
        day = int(date_match.group(3))
        hour = int(date_match.group(4))
        minute = int(date_match.group(5))
        second = int(date_match.group(6))

        dt = datetime.datetime(year, month, day, hour, minute, second)
        pg_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")

        return pg_timestamp

    except Exception as e:
        print(f"無法處理這行資料：{line}\n   錯誤原因：{e}")
        return None

url = "https://od.moi.gov.tw/api/v1/rest/datastore/A01010000C-001309-001?limit=100"
response = requests.get(url)
data = response.json()
data = data["result"]["records"]

# connect to postgres database
conn = psycopg2.connect(
    dbname="nutn",
    user="nutn",
    password="nutn@password",
    host="10.0.2.15",
    port="5432",
)
cur = conn.cursor()


for item in data:
    print(f'{parse_line(item["ACCYMD"])} {item["PLACE"]} {item["CARTYPE"]}')

    happened_at = parse_line(item["ACCYMD"])
    location = item["PLACE"]
    description = item["CARTYPE"]

    if happened_at:
        cur.execute(
            "INSERT INTO accidents (happened_at, location, description) VALUES (%s, %s, %s)",
            (happened_at, location, description)
        )

conn.commit()
cur.close()
conn.close()