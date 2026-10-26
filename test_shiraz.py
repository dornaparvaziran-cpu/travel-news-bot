import requests
import json

def main():
    print("Finding City ID for Mashhad...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }
    
    # این آدرس معمولاً لیست شهرها رو برمی‌گردونه (روش رایج در این نوع APIها)
    urls_to_try = [
        "https://www.flytoday.ir/api/gateway/V1/geo/cities?countryCode=IR",
        "https://www.flytoday.ir/api/gateway/V1/hotel/cities?countryCode=IR",
        "https://www.flytoday.ir/api/gateway/V1/geo/city?countryCode=IR"
    ]
    
    for url in urls_to_try:
        print(f"\nTrying URL: {url}")
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.ok:
                data = r.json()
                # جستجوی کلمه مشهد در کل پاسخ JSON
                json_str = json.dumps(data, ensure_ascii=False)
                if "مشهد" in json_str or "Mashhad" in json_str:
                    print("✅ Found Mashhad in this response!")
                    # چاپ بخشی از داده که شامل مشهد هست
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
                    break
                else:
                    print("Mashhad not found in this URL.")
            else:
                print(f"❌ Failed: {r.status_code}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
