import requests
import json
from datetime import datetime, timedelta

def main():
    print("Testing FlyToday API - Root Keys...")
    
    url = "https://www.flytoday.ir/api/gateway/V3/hotel/Availability?pageNumber=1&pageSize=25&sortMode=Featured"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    payload = {
        "checkIn": tomorrow,
        "checkOut": day_after,
        "hotelId": None,
        "cityId": 10, # مشهد
        "cityName": "",
        "countryCode": "IR",
        "dateLang": "fa",
        "hotelName": "",
        "isDomestic": True,
        "isJalali": True,
        "key": "",
        "NationalityId": "IR",
        "occupancies": [{"adultCount": 1, "childCount": 0, "childAges": []}]
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if r.ok:
            data = r.json()
            
            print("\n--- ROOT KEYS ---")
            for key in data.keys():
                print(f"- {key}")
                
            # چک کردن اینکه آیا لیست هتل‌ها با اسمشون توی روت هست یا نه
            if "hotels" in data:
                print("\n--- HOTELS LIST (first 2) ---")
                print(json.dumps(data["hotels"][:2], indent=2, ensure_ascii=False))
            elif "properties" in data:
                print("\n--- PROPERTIES LIST (first 2) ---")
                print(json.dumps(data["properties"][:2], indent=2, ensure_ascii=False))
            else:
                print("\n(No 'hotels' or 'properties' list in root)")
                
        else:
            print(f"❌ Error: {r.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
