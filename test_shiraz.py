import requests
import json

def main():
    print("Testing FlyToday API - Getting Hotel Name by ID...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }
    
    hotel_id = 209 # همون آیدی که از لاگ قبلی گرفتیم
    
    # چند آدرس مختلف رو تست می‌کنیم (چون بعضی‌ها نیاز به POST دارن)
    urls_to_try = [
        f"https://www.flytoday.ir/api/gateway/V1/hotel/Portfolio?hotelId={hotel_id}",
        f"https://www.flytoday.ir/api/gateway/V1/hotel/Details?hotelId={hotel_id}",
        f"https://www.flytoday.ir/api/gateway/V1/hotel/Info?hotelId={hotel_id}"
    ]
    
    for url in urls_to_try:
        print(f"\nTrying URL: {url}")
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.ok:
                data = r.json()
                print("✅ Success!")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
                break
            else:
                print(f"❌ Failed: {r.status_code}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
