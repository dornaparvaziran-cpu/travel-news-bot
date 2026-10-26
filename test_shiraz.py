import requests
import json
from datetime import datetime, timedelta

def main():
    print("Testing FlyToday API - Extracting Hotel Details...")
    
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
            
            print("\n--- Searching for Hotel Name and Details ---")
            # چاپ تمام کلیدها و مقادیر رشته‌ای (برای پیدا کردن اسم هتل)
            for key, value in first_hotel.items():
                if isinstance(value, str):
                    print(f"{key}: {value}")
                elif isinstance(value, dict):
                    print(f"{key} (dict keys): {list(value.keys())}")
                    
            print("\n--- Checking nested structures ---")
            # گاهی اسم هتل داخل آبجکت 'hotel' یا 'property' هست
            if 'hotel' in first_hotel:
                print("hotel object:", json.dumps(first_hotel['hotel'], ensure_ascii=False)[:500])
                
            # جستجوی کلمه name در کل متن JSON
            import re
            json_str = json.dumps(first_hotel, ensure_ascii=False)
            names = re.findall(r'"name":\s*"([^"]+)"', json_str)
            print("\nAll 'name' values found in first hotel:")
            for n in set(names):
                print(f"- {n}")

        else:
            print(f"❌ Error: {r.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
