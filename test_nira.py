import os
import requests
from datetime import datetime, timedelta

NIRA_USER = os.environ.get("NIRA_USER")
NIRA_PASS = os.environ.get("NIRA_PASS")

# لیست آدرس‌های احتمالی برای تست (دامنه آتا)
BASE_URLS = [
    "https://ra.ataair.ir/AvailabilityJS.jsp",
    "https://ra.ataair.ir/AvailabilityFareJS.jsp",
    "http://ra.ataair.ir:8080/AvailabilityJS.jsp",
    "http://ra.ataair.ir/AvailabilityJS.jsp",
    "https://ataair.ir/AvailabilityJS.jsp"
]

def test_nira_api():
    departure_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    
    for base_url in BASE_URLS:
        print(f"\n--- Testing: {base_url} ---")
        params = {
            "AirLine": "I3", # کد IATA ایرلاین آتا
            "cbSource": "THR", # تهران
            "cbTarget": "MHD", # مشهد
            "cbDay1": "01",
            "cbMonth1": "09",
            "cbAdultQty": 1,
            "cbChildQty": 0,
            "cbInfantQty": 0,
            "OfficeUser": NIRA_USER,
            "OfficePass": NIRA_PASS,
            "DepartureDate": departure_date
        }

        try:
            r = requests.get(base_url, params=params, timeout=15)
            print(f"Status Code: {r.status_code}")
            
            # اگر جواب JSON یا خطای اعتبارسنجی داد، یعنی آدرس درست است
            if r.ok or r.status_code in [400, 401]:
                print("✅ SUCCESS! Found the API endpoint (or at least a valid response).")
                print(r.text[:500]) 
                break 
            else:
                print(f"❌ Failed ({r.status_code})")
                
        except Exception as e:
            print(f"❌ Exception (Timeout/Connection Error)")

if __name__ == "__main__":
    test_nira_api()
