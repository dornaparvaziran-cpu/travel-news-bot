
import os
import requests
import json

BASE_URL = "https://api.ataair.ir/ws1"

AIRLINE = "I3"
ORIGIN = "MHD"
DESTINATION = "TBZ"

DEPARTURE_DATE = "2026-11-22"

ADULTS = 1
CHILDREN = 0
INFANTS = 0


def main():
    print("=== NIRA / ATA Availability Test ===")

    # دریافت اطلاعات از GitHub Secrets
    username = os.environ.get("NIRA_USER")
    password = os.environ.get("NIRA_PASS")

    if not username or not password:
        print("ERROR: NIRA_USERNAME or NIRA_PASSWORD is missing.")
        return

    url = f"{BASE_URL}/AvailabilityJS.jsp"

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

    try:
        print("Connecting to ATA NIRA API...")

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
            print("ERROR: Response is not JSON.")
            print(response.text[:2000])
            return

        flights = data.get("AvailableFlights", [])

        print("\nAPI Response:")
        print(json.dumps(data, ensure_ascii=False, indent=2))

        if flights:
            print(f"\nSUCCESS: Found {len(flights)} flight(s).")

            for i, flight in enumerate(flights, 1):
                print(f"\n--- Flight {i} ---")
                print("Flight No:", flight.get("FlightNo"))
                print("Origin:", flight.get("Origin"))
                print("Destination:", flight.get("Destination"))
                print("Departure:", flight.get("DepartureDateTime"))
                print("Arrival:", flight.get("ArrivalDateTime"))
                print("Classes:", flight.get("ClassesStatus"))
                print("Prices:", flight.get("AdultTotalPrices"))

        else:
            print("No flights found.")
            print("Full API response is shown above.")

    except requests.exceptions.Timeout:
        print("ERROR: API request timed out.")

    except requests.exceptions.HTTPError as e:
        print("HTTP ERROR:", e)
        print(response.text[:2000])

    except requests.exceptions.RequestException as e:
        print("CONNECTION ERROR:", str(e))


if __name__ == "__main__":
    main()
