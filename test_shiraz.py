import requests
import json
from datetime import datetime, timedelta

def main():
    print("Testing FlyToday API - Extracting Hotel Names (POST method)...")
    
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
        
        # ۲. تست API با hotelSearchId به صورت POST
        print("\nStep 2: Sending POST with hotelSearchId...")
        url_test = f"https://www.flytoday.ir/api/gateway/V3/hotel/Availability"
        
        # چند حالت مختلف برای فرستادن hotelSearchId
        test_payloads = [
            {"hotelSearchId": hotel_search_id},
            {"hotelSearchId": hotel_search_id, "pageNumber": 1, "pageSize": 25},
            {"searchId": hotel_search_id}
        ]
        
        for i, payload in enumerate(test_payloads):
            print(f"\n--- Test {i+1}: {payload} ---")
            r_test = requests.post(url_test, headers=headers, json=payload, timeout=30)
            
            if r_test.ok:
                print("✅ Success!")
                data_test = r_test.json()
                itineraries = data_test.get("pricedItineraries", [])
                if itineraries:
                    print(f"Found {len(itineraries)} hotels.")
                    # چاپ کل JSON اولین هتل برای دیدن اسم
                    print("\n--- Full JSON of First Itinerary ---")
                    print(json.dumps(itineraries[0], indent=2, ensure_ascii=False)[:3000])
                else:
                    print("No itineraries in response.")
            else:
                print(f"❌ Failed: {r_test.status_code} - {r_test.text[:200]}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
