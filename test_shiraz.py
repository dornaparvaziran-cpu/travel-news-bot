import requests
import json
from datetime import datetime, timedelta

def main():
    print("Testing FlyToday API - Extracting Hotel Names from Availability...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    # ۱. گرفتن hotelSearchId
    print("Step 1: Getting hotelSearchId...")
    url_avail = "https://www.flytoday.ir/api/gateway/V3/hotel/Availability?pageNumber=1&pageSize=25&sortMode=Featured"
    payload_avail = {
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
        r_avail = requests.post(url_avail, headers=headers, json=payload_avail, timeout=30)
        if not r_avail.ok:
            print(f"❌ Availability Error: {r_avail.status_code}")
            return
            
        data_avail = r_avail.json()
        hotel_search_id = data_avail.get("hotelSearchId")
        print(f"✅ Got hotelSearchId: {hotel_search_id}")
        
        # ۲. درخواست به API Availability با پارامتر hotelSearchId
        print("\nStep 2: Fetching with hotelSearchId...")
        url_avail_2 = f"https://www.flytoday.ir/api/gateway/V3/hotel/Availability?hotelSearchId={hotel_search_id}"
        
        # چون ممکنه این درخواست از نوع GET یا POST باشه، هر دو رو تست می‌کنیم
        r_avail_2 = requests.get(url_avail_2, headers=headers, timeout=30)
        
        if r_avail_2.ok:
            print("✅ GET worked!")
            data_2 = r_avail_2.json()
            itineraries = data_2.get("pricedItineraries", [])
            if itineraries:
                print(f"\nFound {len(itineraries)} itineraries.")
                # چاپ کل JSON اولین هتل برای دیدن اسم
                print("\n--- Full JSON of First Itinerary ---")
                print(json.dumps(itineraries[0], indent=2, ensure_ascii=False)[:3000])
            else:
                print("No itineraries found.")
        else:
            print(f"❌ GET failed: {r_avail_2.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
