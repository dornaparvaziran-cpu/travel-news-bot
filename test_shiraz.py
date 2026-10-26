import requests
import json

def main():
    print("Testing Portfolio API with citySlug and different parameters...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }
    
    url_portfolio = "https://www.flytoday.ir/api/gateway/V1/hotel/Portfolio"
    
    # چند حالت مختلف برای پیدا کردن هتل‌های مشهد
    test_payloads = [
        {"citySlug": "mashhad", "pageNumber": 1, "pageSize": 5},
        {"cityId": 1, "pageNumber": 1, "pageSize": 5},
        {"cityId": 2, "pageNumber": 1, "pageSize": 5},
        {"cityId": 3, "pageNumber": 1, "pageSize": 5},
        {"cityId": 11, "pageNumber": 1, "pageSize": 5},
        {"cityName": "مشهد", "pageNumber": 1, "pageSize": 5}
    ]
    
    for i, payload in enumerate(test_payloads):
        print(f"\n--- Test {i+1}: {payload} ---")
        try:
            r = requests.post(url_portfolio, headers=headers, json=payload, timeout=15)
            if r.ok:
                data = r.json()
                hotel_info = data.get("hotelInfo", [])
                if hotel_info:
                    first_hotel = hotel_info[0]
                    name = first_hotel.get("name", "")
                    city = first_hotel.get("citySlug", "")
                    print(f"✅ Success! First hotel: {name} (City: {city})")
                    # اگر اسم هتل فارسی بود یا مربوط به مشهد بود، متوقف شو
                    if "مشهد" in name or city == "mashhad":
                        print("🎯 Found Mashhad hotels! Here is the full data for first hotel:")
                        print(json.dumps(first_hotel, indent=2, ensure_ascii=False))
                        break
                else:
                    print("⚠️ No hotelInfo in response.")
            else:
                print(f"❌ Failed: {r.status_code}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
