
import os
import json
import requests

print("=== NIRA / ATA AvailabilityFare Test ===")

# Credentials from GitHub Secrets
username = os.environ.get("NIRA_USER")
password = os.environ.get("NIRA_PASS")

if not username or not password:
    print("ERROR: NIRA_USER or NIRA_PASS is missing.")
    raise SystemExit(1)

# ATA API settings
BASE_URL = "https://api.ataair.ir/ws1"
AIRLINE = "I3"

# Flight information
ORIGIN = "MHD"
DESTINATION = "TBZ"
DEPARTURE_DATE = "2026-11-22"

# Passenger count
ADULTS = 1
CHILDREN = 0
INFANTS = 0

params = {
    "AirLine": AIRLINE,
    "cbSource": ORIGIN,
    "cbTarget": DESTINATION,
    "cbDay1": "",
    "cbMonth1": "",
    "DepartureDate": DEPARTURE_DATE,
    "cbAdultQty": ADULTS,
    "cbChildQty": CHILDREN,
    "cbInfantQty": INFANTS,
    "OfficeUser": username,
    "OfficePass": password,
}

url = f"{BASE_URL}/AvailabilityFareJS.jsp"

try:
    print("Connecting to ATA AvailabilityFare API...")

    response = requests.get(
        url,
        params=params,
        timeout=45
    )

    print("HTTP Status:", response.status_code)
    response.raise_for_status()

    try:
        data = response.json()
    except ValueError:
        print("ERROR: API did not return valid JSON.")
        print(response.text[:2000])
        raise SystemExit(1)

    print("\nAPI Response:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    flights = data.get("AvailableFlights", [])

    if not flights:
        print("\nNo available flights found.")
        raise SystemExit(0)

    print(f"\nSUCCESS: Found {len(flights)} flight(s).")

    for index, flight in enumerate(flights, start=1):
        print(f"\n--- Flight {index} ---")
        print("Flight No:", flight.get("FlightNo"))
        print("Origin:", flight.get("Origin"))
        print("Destination:", flight.get("Destination"))
        print("Departure:", flight.get("DepartureDateTime"))
        print("Arrival:", flight.get("ArrivalDateTime"))

        classes = flight.get("ClassesStatus", [])

        print("\n--- Available Classes ---")

        if isinstance(classes, list):
            for item in classes:
                print(
                    "Class:", item.get("FlightClass"),
                    "| Capacity:", item.get("Cap"),
                    "| Price:", item.get("Price"),
                    "| Currency:", item.get("CurrencyCode")
                )
        else:
            print(classes)

except requests.exceptions.Timeout:
    print("ERROR: API request timed out.")

except requests.exceptions.RequestException as error:
    print("HTTP/API ERROR:", error)

except Exception as error:
    print("ERROR:", str(error))
