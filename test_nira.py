import os
import requests
from datetime import datetime, timedelta

NIRA_USER = os.environ.get("NIRA_USER")
NIRA_PASS = os.environ.get("NIRA_PASS")
NIRA_BASE_URL = os.environ.get("NIRA_BASE_URL")

def test_nira_api():
    if not NIRA_BASE_URL:
        print("❌ NIRA_BASE_URL is missing!")
        return

    # تنظیم پارامترها بر اساس مستندات نیرا
    params = {
        "AirLine": "*",       # * یعنی همه ایرلاین‌ها
        "cbSource": "THR",    # مبدا: تهران
        "cbTarget": "MHD",    # مقصد: مشهد
        "cbDay1": "01",       # تاریخ شمسی (روز)
        "cbMonth1": "09",     # تاریخ شمسی (ماه)
        "cbAdultQty": 1,
        "cbChildQty": 0,
        "cbInfantQty": 0,
        "OfficeUser": NIRA_USER,
        "OfficePass": NIRA_PASS,
        "DepartureDate": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d") # تاریخ میلادی
    }

    print(f"Sending request to: {NIRA_BASE_URL}")
    try:
        r = requests.get(NIRA_BASE_URL, params=params, timeout=30)
        print(f"Status Code: {r.status_code}")
        
        if r.ok:
            print("✅ Nira API connected successfully!")
            # چاپ ۲۰۰۰ کاراکتر اول پاسخ برای بررسی
            print(r.text[:2000])
        else:
            print("❌ Error response:", r.text)
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_nira_api()
