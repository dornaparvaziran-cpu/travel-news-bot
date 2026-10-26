import requests
import json
from datetime import datetime, timedelta

def main():
    print("Testing FlyToday API - Full JSON Dump...")
    
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
            itineraries = data.get("pricedItineraries", [])
            
            if not itineraries:
                print("No hotels found.")
                return
                
            first_hotel = itineraries[0]
            
            # 🌟 چاپ کل JSON اولین هتل
            print("\n--- FULL JSON OF FIRST HOTEL ---")
            print(json.dumps(first_hotel, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ Error: {r.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
