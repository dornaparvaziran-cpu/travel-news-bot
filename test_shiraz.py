import requests
import json
from datetime import datetime, timedelta

def main():
    print("Testing FlyToday API - Fetching Accommodations...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    # ۱. گرفتن hotelSearchId از API اول
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
        
        # ۲. درخواست به API accommodations برای گرفتن اسم هتل‌ها
        print("\nStep 2: Fetching Accommodations using the ID...")
        url_acc = "https://www.flytoday.ir/api/gateway/V1/hotel/accommodations"
        
        # گاهی این درخواست از نوع POST است و گاهی GET. هر دو رو تست می‌کنیم.
        
        # تلاش اول: POST
        print("Trying POST method...")
        payload_acc = {
            "hotelSearchId": hotel_search_id,
            "pageNumber": 1,
            "pageSize": 50
        }
        r_acc = requests.post(url_acc, headers=headers, json=payload_acc, timeout=30)
        
        if not r_acc.ok:
            print(f"POST failed ({r_acc.status_code}). Trying GET method...")
            # تلاش دوم: GET
            params_acc = {
                "hotelSearchId": hotel_search_id,
                "pageNumber": 1,
                "pageSize": 50
            }
            r_acc = requests.get(url_acc, headers=headers, params=params_acc, timeout=30)
            
        if r_acc.ok:
            print("✅ Accommodations API worked!")
            acc_data = r_acc.json()
            
            # چاپ ۳۰۰۰ کاراکتر اول برای دیدن ساختار اسم و ستاره
            print("\n--- Response (First 3000 chars) ---")
            print(json.dumps(acc_data, indent=2, ensure_ascii=False)[:3000])
        else:
            print(f"❌ Accommodations API failed: {r_acc.status_code} - {r_acc.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
