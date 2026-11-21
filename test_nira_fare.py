
import os
import sys
import json
import requests

BASE_URL = "https://api.ataair.ir/ws1"
FARE_URL = f"{BASE_URL}/FareJS.jsp"

NIRA_USER = os.getenv("NIRA_USER")
NIRA_PASS = os.getenv("NIRA_PASS")

if not NIRA_USER or not NIRA_PASS:
    print("ERROR: NIRA_USER or NIRA_PASS is missing.")
    sys.exit(1)

# اطلاعات پرواز آزمایشی
params = {
    "AirLine": "I3",
    "Route": "MHD-TBZ",
    "RBD": "A",
    "FlightNO": "5616",
    "DepartureDate": "2026-11-22",
    "OfficeUser": NIRA_USER,
    "OfficePass": NIRA_PASS,
}

try:
    print("=== NIRA / ATA Fare Test ===")
    print("Requesting fare information...")
    print("Flight: I3 5616")
    print("Route: MHD-TBZ")
    print("Class: A")
    print("Date: 2026-11-22")

    response = requests.get(
        FARE_URL,
        params=params,
        timeout=30
    )

    print("\nHTTP Status:", response.status_code)
    response.raise_for_status()

    try:
        data = response.json()
    except ValueError:
        print("Invalid JSON response:")
        print(response.text)
        sys.exit(1)

    print("\nFare Response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    if data.get("ErrorCode") == "-1":
        print("\nFARE FAILED")
        print("Error:", data.get("EN"))
        print("Message:", data.get("FA"))
        sys.exit(1)

    print("\nSUCCESS: Fare response received.")

    # نمایش نرخ‌ها
    fields = [
        "AdultFare",
        "AdultTotalPrice",
        "ChildFare",
        "ChildTotalPrice",
        "InfantFare",
        "InfantTotalPrice",
        "AdultTaxes",
        "ChildTaxes",
        "InfantTaxes",
        "BaggageAllowanceWeight",
        "BaggageAllowancePieces",
        "CRCNRules",
    ]

    print("\n--- Fare Details ---")

    for field in fields:
        if field in data:
            print(f"{field}: {data[field]}")

except requests.exceptions.RequestException as error:
    print("\nREQUEST ERROR:", error)
    sys.exit(1)
