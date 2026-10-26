import requests
import json
from datetime import datetime, timedelta

def main():
    print("Testing FlyToday API...")
    
    # آدرس API
    url = "https://www.flytoday.ir/api/gateway/V3/hotel/Availability?pageNumber=1&pageSize=25&sortMode=Featured"
    
    # هدرها (برای اینکه سایت فکر کنه ما یک مرورگر هستیم)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }
    
    # تاریخ‌ها (فردا و پس فردا)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    # داده‌هایی که فرستادی (Payload)
    payload = {
        "checkIn": tomorrow,
        "checkOut": day_after,
        "hotelId": None,
        "cityId": 10, # کد شهر 10 معمولاً مشهد هست
        "cityName": "",
        "countryCode": "IR",
        "dateLang": "fa",
        "hotelName": "",
        "isDomestic": True,
        "isJalali": True,
        "key": "",
        "NationalityId": "IR",
        "occupancies": [
            {
                "adultCount": 1,
                "childCount": 0,
                "childAges": []
            }
        ]
    }
    
    print(f"Sending POST request for dates: {tomorrow} to {day_after}")
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {r.status_code}")
        
        if r.ok:
            data = r.json()
            print("\n✅ Response received successfully!")
            # چاپ ۲۰۰۰ کاراکتر اول از پاسخ برای دیدن ساختار
            print("--- First 2000 chars of response ---")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
        else:
            print(f"❌ Error: {r.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
