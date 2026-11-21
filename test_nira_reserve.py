
import os
import sys
import json
import requests

BASE_URL = "https://api.ataair.ir/ws1"
RESERVE_URL = f"{BASE_URL}/ReservJS"

def get_env(name):
    value = os.getenv(name)
    if not value:
        print(f"ERROR: Missing environment variable: {name}")
        sys.exit(1)
    return value

# اعتبارنامه‌ها
nira_user = get_env("NIRA_USER")
nira_pass = get_env("NIRA_PASS")

# اطلاعات مسافر؛ از GitHub Secrets خوانده می‌شوند
first_name = get_env("PASSENGER_FIRST_NAME")
last_name = get_env("PASSENGER_LAST_NAME")
age = get_env("PASSENGER_AGE")
passenger_id = get_env("PASSENGER_ID_FIELD")
contact = get_env("PASSENGER_CONTACT")

# تأیید صریح برای جلوگیری از رزرو ناخواسته
if os.getenv("RESERVE_CONFIRM") != "YES":
    print("RESERVATION NOT SENT.")
    print("Set RESERVE_CONFIRM=YES to authorize the request.")
    sys.exit(0)

if not age.isdigit():
    print("ERROR: PASSENGER_AGE must be numeric.")
    sys.exit(1)

params = {
    "AirLine": "I3",
    "cbSource": "MHD",
    "cbTarget": "TBZ",
    "FlightClass": "A",
    "FlightNo": "5616",
    "DepartureDate": "2026-11-22",
    "Day": "",
    "Month": "",
    "No": "1",

    "edtName1": first_name,
    "edtLast1": last_name,
    "edtAge1": age,
    "edtID1": passenger_id,
    "edtContact": contact,

    "OfficeUser": nira_user,
    "OfficePass": nira_pass,
}

try:
    print("=== NIRA / ATA Reservation ===")
    print("Flight: I3 5616")
    print("Route: MHD-TBZ")
    print("Class: A")
    print("Passengers: 1")
    print("Sending reservation request...")

    response = requests.post(
        RESERVE_URL,
        data=params,
        timeout=45
    )

    print("HTTP Status:", response.status_code)
    response.raise_for_status()

    try:
        result = response.json()
    except ValueError:
        print("Non-JSON response:")
        print(response.text[:3000])
        sys.exit(1)

    # اطلاعات حساس مسافر و اعتبارنامه‌ها چاپ نمی‌شوند
    print("\nReservation Response:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if isinstance(result, dict):
        if result.get("Error") == "No Err":
            print("\nSUCCESS: Reservation accepted.")
            print("PNR:", result.get("PNR", "Not returned"))
        else:
            print("\nReservation was not confirmed.")
            print("Please review the response.")

except requests.exceptions.RequestException as error:
    print("\nREQUEST ERROR:", str(error))
    sys.exit(1)
