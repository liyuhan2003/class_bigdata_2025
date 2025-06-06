import requests
import json
import re, datetime
import psycopg2
from collections import OrderedDict

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

url = "https://od.moi.gov.tw/api/v1/rest/datastore/A01010000C-001309-001?limit=10000"
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

cur.execute("DROP TABLE IF EXISTS accidents")
cur.execute("DROP TABLE IF EXISTS vehicles")
cur.execute("DROP TABLE IF EXISTS accident_vehicles")

cur.execute("""
    CREATE TABLE accidents (
        id SERIAL PRIMARY KEY,
        happened_at TIMESTAMP NOT NULL,
        location TEXT NOT NULL
    )
""")

cur.execute("""
    CREATE TABLE vehicles (
        id SERIAL PRIMARY KEY,
        vehicles_name TEXT
    )
""")

cur.execute("""
    CREATE TABLE accident_vehicles (
        id SERIAL PRIMARY KEY,
        accident_id INTEGER  NOT NULL,
        vehicle_id INTEGER  NOT NULL
    );
""")


vehicles_seen = OrderedDict()

for i, item in enumerate(data):
    if i == 0:
        continue
    print(f'{parse_line(item["ACCYMD"])} {item["PLACE"]} {item["CARTYPE"]}')

    happened_at = parse_line(item["ACCYMD"])
    location = item["PLACE"]
    description = item["CARTYPE"]



    if happened_at:
        cur.execute(
            "INSERT INTO accidents (id, happened_at, location) VALUES (%s, %s, %s)",
            (i, happened_at, location)
        )

        description_list = description.split(';')

        for description_item in description_list:
            vehicle = description_item.strip()
            if vehicle and vehicle not in vehicles_seen:
                vehicles_seen[vehicle] = vehicle

            if vehicle:
                vehicle_id = list(vehicles_seen.keys()).index(vehicle) + 1
            else:
                vehicle_id = 0

            cur.execute(
                "INSERT INTO accident_vehicles (accident_id, vehicle_id) VALUES (%s, %s)",
                (i, vehicle_id)
            )

for i, vehicle_name in enumerate(vehicles_seen, start=1):
    cur.execute(
        "INSERT INTO vehicles (id, vehicles_name) VALUES (%s, %s)",
        (i, vehicle_name)
    )
conn.commit()
cur.close()
conn.close()