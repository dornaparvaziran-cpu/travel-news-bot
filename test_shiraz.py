import requests
import json

def main():
    print("Testing TKTFLY (Charter724) API...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    # چند آدرس احتمالی برای دریافت اطلاعات هتل
    urls_to_try = [
        "https://ticket.tktfly.ir/api/hotel/search",
        "https://ticket.tktfly.ir/api/hotels",
        "https://ticket.tktfly.ir/hotel/api",
        "https://ticket.tktfly.ir/api/v1/hotels"
    ]
    
    for url in urls_to_try:
        print(f"\nTrying: {url}")
        try:
            r = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {r.status_code}")
            if r.ok:
                print("✅ Success! Response:")
                print(r.text[:500]) # چاپ ۵۰۰ کاراکتر اول
                break
            else:
                print(f"Response: {r.text[:200]}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
