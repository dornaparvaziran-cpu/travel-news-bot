import requests
import re

def main():
    print("Testing Alibaba...")
    
    # آدرس صفحه هتل‌های مشهد در علی‌بابا
    url = "https://www.alibaba.ir/hotel/mashhad"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=20)
        print(f"Status Code: {r.status_code}")
        
        if r.ok:
            print("Page loaded successfully!")
            
            # پیدا کردن قیمت‌ها با روش ساده
            prices = re.findall(r'([\d,]+)\s*تومان', r.text)
            print(f"Found {len(prices)} prices on the page.")
            
            if prices:
                print("First 10 prices:")
                for p in prices[:10]:
                    print(f"- {p} تومان")
            else:
                print("No prices found in HTML (maybe the site uses JavaScript).")
        else:
            print(f"Error: {r.status_code}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()