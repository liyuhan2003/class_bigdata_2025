import requests
import psycopg2
from collections import Counter

# 抓取資料
url = "https://data.moa.gov.tw/Service/OpenData/TransService.aspx?UnitId=IFJomqVzyB0i&IsTransData=1"
response = requests.get(url)
data = response.json()

# 建立 PostgreSQL 連線
conn = psycopg2.connect(
    dbname="nutn",
    user="nutn",
    password="nutn@password",
    host="10.0.2.15",
    port="5432"
)
cur = conn.cursor()

# 建立主表
cur.execute("DROP TABLE IF EXISTS lost_animals")
cur.execute("""
    CREATE TABLE lost_animals (
        id SERIAL PRIMARY KEY,
        lost_date TEXT,
        lost_location TEXT,
        contact_number TEXT,
        animal_breed TEXT
    )
""")

# 初始化統計與去重用結構
city_counter = Counter()
breed_counter = Counter()
year_counter = Counter()
seen_records = set()

# 同義縣市標準化對照表
city_alias_map = {
    "臺北市": "台北市",
    "台北市": "台北市",
    "臺中市": "台中市",
    "台中市": "台中市",
    "臺南市": "台南市",
    "台南市": "台南市",
    "臺東縣": "台東縣",
    "台東縣": "台東縣",
    "臺中縣": "台中市",
    "臺北縣": "新北市",
}

# 處理每筆資料
for item in data:
    lost_date = str(item.get("遺失時間", "")).strip()
    lost_location = str(item.get("遺失地點") or item.get("遺失地址") or "").strip()
    contact_number = str(item.get("連絡電話", "")).strip()
    animal_breed = str(item.get("品種", "")).strip()

    # 判斷是否重複
    record_key = (lost_date, lost_location, contact_number, animal_breed)
    if record_key in seen_records:
        continue
    seen_records.add(record_key)

    # 寫入主表
    cur.execute("""
        INSERT INTO lost_animals (lost_date, lost_location, contact_number, animal_breed)
        VALUES (%s, %s, %s, %s)
    """, (lost_date, lost_location, contact_number, animal_breed))

    # 統計城市
    if lost_location:
        raw_city = lost_location[:3]
        city = city_alias_map.get(raw_city, raw_city)
        city_counter[city] += 1

    # 統計品種
    if animal_breed:
        breed_counter[animal_breed] += 1
    # 統計年份（從 lost_date 擷取年）
    if lost_date and len(lost_date) >= 4:
        year = lost_date[:4]
        if year.isdigit():
            year_counter[year] += 1    

# 建立 city_statistics 表
cur.execute("DROP TABLE IF EXISTS city_statistics")
cur.execute("""
    CREATE TABLE city_statistics (
        id SERIAL PRIMARY KEY,
        city TEXT NOT NULL,
        count INTEGER NOT NULL
    )
""")
for city, count in city_counter.most_common():
    cur.execute("INSERT INTO city_statistics (city, count) VALUES (%s, %s)", (city, count))

# 建立 breed_statistics 表
cur.execute("DROP TABLE IF EXISTS breed_statistics")
cur.execute("""
    CREATE TABLE breed_statistics (
        id SERIAL PRIMARY KEY,
        breed TEXT NOT NULL,
        count INTEGER NOT NULL
    )
""")
for breed, count in breed_counter.most_common():
    cur.execute("INSERT INTO breed_statistics (breed, count) VALUES (%s, %s)", (breed, count))

# 建立 year_statistics 表
cur.execute("DROP TABLE IF EXISTS year_statistics")
cur.execute("""
    CREATE TABLE year_statistics (
        id SERIAL PRIMARY KEY,
        year TEXT NOT NULL,
        count INTEGER NOT NULL
    )
""")

for year, count in year_counter.most_common():
    cur.execute("INSERT INTO year_statistics (year, count) VALUES (%s, %s)", (year, count))

# 完成寫入
conn.commit()
cur.close()
conn.close()

print("走失動物資料與統計已匯入資料庫")
