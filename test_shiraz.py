import requests
import json
from datetime import datetime, timedelta

def main():
    print("Testing FlyToday API - Final Attempt...")
    
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
        
        # ۲. تست API با آدرس جدید (که فرستادی)
        print(f"\nStep 2: Fetching from {url_avail}/{hotel_search_id} ...")
        url_test = f"https://www.flytoday.ir/api/gateway/V3/hotel/Availability/{hotel_search_id}"
        
        r_test = requests.get(url_test, headers=headers, timeout=30)
        
        if r_test.ok:
            print("✅ GET worked!")
            data_test = r_test.json()
            
            # چاپ کل JSON برای دیدن اسم و آیدی هتل‌ها
            print("\n--- Full JSON Response (First 3000 chars) ---")
            print(json.dumps(data_test, indent=2, ensure_ascii=False)[:3000])
        else:
            print(f"❌ GET failed: {r_test.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
