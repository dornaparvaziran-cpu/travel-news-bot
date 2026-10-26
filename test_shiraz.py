import requests
import json
from datetime import datetime, timedelta

def main():
    print("Testing FlyToday API - Fetching Accommodations...")
    
    # ۱. درخواست اول برای گرفتن قیمت‌ها
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
        if not r.ok:
            print(f"❌ Availability Error: {r.status_code} - {r.text}")
            return
            
        data = r.json()
        hotel_search_id = data.get("hotelSearchId")
        print(f"✅ Got hotelSearchId: {hotel_search_id}")
        
        # ۲. حالا سعی می‌کنیم با استفاده از این ID، اسم هتل‌ها رو بگیریم
        # ما چند آدرس احتمالی رو تست می‌کنیم
        possible_urls = [
            f"https://www.flytoday.ir/api/gateway/V3/hotel/accommodations?hotelSearchId={hotel_search_id}",
            f"https://www.flytoday.ir/api/gateway/v3/hotel/accommodations?hotelSearchId={hotel_search_id}",
            f"https://www.flytoday.ir/api/gateway/accommodations?hotelSearchId={hotel_search_id}"
        ]
        
        for test_url in possible_urls:
            print(f"\nTrying URL: {test_url}")
            try:
                r_acc = requests.get(test_url, headers=headers, timeout=10)
                if r_acc.ok:
                    print("✅ SUCCESS! Status 200.")
                    acc_data = r_acc.json()
                    
                    # چاپ ۱۰۰۰ کاراکتر اول برای دیدن ساختار
                    print(json.dumps(acc_data, indent=2, ensure_ascii=False)[:1000])
                    break 
                else:
                    print(f"❌ Failed: {r_acc.status_code}")
            except Exception as e:
                print(f"❌ Exception: {e}")
                
    except Exception as e:
        print(f"❌ Main Exception: {e}")

if __name__ == "__main__":
    main()
