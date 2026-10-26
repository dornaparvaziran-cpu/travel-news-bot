import requests
import json
from datetime import datetime, timedelta

def main():
    print("Testing FlyToday API - Fetching Hotel Portfolio...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    # ۱. گرفتن hotelSearchId و hotelId یک هتل از API اول
    print("Step 1: Getting hotelSearchId and a sample hotelId...")
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
        itineraries = data_avail.get("pricedItineraries", [])
        
        if not itineraries:
            print("❌ No hotels found in Availability.")
            return
            
        sample_hotel_id = itineraries[0].get("hotelId")
        print(f"✅ Got hotelSearchId: {hotel_search_id}")
        print(f"✅ Sample hotelId: {sample_hotel_id}")
        
        # ۲. تست API پورتفولیو
        print("\nStep 2: Testing Portfolio API...")
        url_portfolio = "https://www.flytoday.ir/api/gateway/V1/hotel/Portfolio"
        
        # چند روش برای فرستادن پارامترها تست می‌کنیم
        # روش اول: با پارامترهای URL (GET)
        print("Trying GET with params...")
        params = {"hotelId": sample_hotel_id, "hotelSearchId": hotel_search_id}
        r_port = requests.get(url_portfolio, headers=headers, params=params, timeout=30)
        
        if not r_port.ok:
            print(f"GET failed ({r_port.status_code}). Trying POST...")
            # روش دوم: با JSON (POST)
            r_port = requests.post(url_portfolio, headers=headers, json=params, timeout=30)
            
        if r_port.ok:
            print("✅ Portfolio API worked!")
            port_data = r_port.json()
            print("\n--- Response (First 2000 chars) ---")
            print(json.dumps(port_data, indent=2, ensure_ascii=False)[:2000])
        else:
            print(f"❌ Portfolio API failed: {r_port.status_code} - {r_port.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
