import requests
import os

def main():
    API_KEY = os.environ.get("PARSE_KEY")
    if not API_KEY:
        print("API KEY NOT FOUND!")
        return
        
    print("Testing Snapptrip API...")
    
    # آدرس API جستجوی هتل در مشهد
    url = "https://api.parse.bot/snapptrip/hotels/search"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "city": "مشهد",
        "checkin": "2026-10-28",
        "checkout": "2026-10-29"
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status Code: {r.status_code}")
        
        if r.ok:
            res_data = r.json()
            print("Response:")
            print(res_data)
        else:
            print(f"Error: {r.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()