
import os
import requests
import json
import sys

BASE_URL = "https://api.ataair.ir/ws1"
FARE_URL = f"{BASE_URL}/FareJS.jsp"

NIRA_USER = os.getenv("NIRA_USER")
NIRA_PASS = os.getenv("NIRA_PASS")

if not NIRA_USER or not NIRA_PASS:
    print("ERROR: NIRA_USER or NIRA_PASS is missing.")
    sys.exit(1)

# اطلاعات پرواز آزمایشی قبلی
params = {
    "Airline": "I3",
    "cbSource": "MHD",
    "cbTarget": "TBZ",
    "DepartureDate": "2026-11-22",
    "FlightNo": "5616",
    "OfficeUser": NIRA_USER,
    "OfficePass": NIRA_PASS,
}

try:
    print("Sending Fare request...")

    response = requests.get(
        FARE_URL,
        params=params,
        timeout=30
    )

    print("HTTP Status:", response.status_code)
    response.raise_for_status()

    try:
        data = response.json()
        print("\nFare response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except ValueError:
        print("\nNon-JSON response:")
        print(response.text)

except requests.exceptions.RequestException as error:
    print("Request failed:", error)
    sys.exit(1)
