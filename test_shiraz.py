import requests
import json

def main():
    print("Testing FlyToday Portfolio API with CityId...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }
    
    url_portfolio = "https://www.flytoday.ir/api/gateway/V1/hotel/Portfolio"
    
    # این بار cityId رو می‌فرستیم (مشهد = 10)
    payload = {
        "cityId": 10,
        "pageNumber": 1,
        "pageSize": 100
    }
    
    print(f"Sending POST with cityId=10...")
    try:
        r = requests.post(url_portfolio, headers=headers, json=payload, timeout=30)
        
        if r.ok:
            print("✅ Portfolio API worked!")
            data = r.json()
            
            # چاپ ۳۰۰۰ کاراکتر اول برای دیدن اسم هتل‌ها و ستاره‌ها
            print("\n--- Response (First 3000 chars) ---")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
        else:
            print(f"❌ API failed: {r.status_code}")
            print(f"Response: {r.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
