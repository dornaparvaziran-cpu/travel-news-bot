import requests
import json
from datetime import datetime, timedelta

def main():
    print("Testing FlyToday API - Digging deeper...")
    
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
            
            print("\n--- CHECKING additionalInfo ---")
            if "additionalInfo" in data:
                print(json.dumps(data["additionalInfo"], indent=2, ensure_ascii=False)[:1500])
                
            print("\n--- CHECKING geoLocations ---")
            if "geoLocations" in data:
                print(json.dumps(data["geoLocations"], indent=2, ensure_ascii=False)[:1500])
                
            print("\n--- CHECKING filter ---")
            if "filter" in data:
                print(json.dumps(data["filter"], indent=2, ensure_ascii=False)[:1500])
                
            # اگر اسم هتل پیدا نشد، با استفاده از hotelId یک درخواست دیگه می‌زنیم
            itineraries = data.get("pricedItineraries", [])
            if itineraries:
                hotel_id = itineraries[0].get("hotelId")
                print(f"\n--- Trying to get details for Hotel ID: {hotel_id} ---")
                # این آدرس رو حدس می‌زنیم، شاید درست باشه
                details_url = f"https://www.flytoday.ir/api/gateway/v3/hotel/{hotel_id}"
                r_details = requests.get(details_url, headers=headers, timeout=10)
                if r_details.ok:
                    print("✅ Details URL worked!")
                    print(json.dumps(r_details.json(), indent=2, ensure_ascii=False)[:1000])
                else:
                    print(f"❌ Details URL failed: {r_details.status_code}")
                
        else:
            print(f"❌ Error: {r.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
