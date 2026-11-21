
import requests
import json
from getpass import getpass

# آدرس پایه API آتا
BASE_URL = "https://api.ataair.ir/ws1"

# اطلاعات جست‌وجوی پرواز
AIRLINE = "I3"
ORIGIN = "UGT"
DESTINATION = "TTQ"

# تاریخ میلادی پرواز؛ این مقدار را تغییر بده
DEPARTURE_DATE = "2026-12-01"

ADULTS = 1
CHILDREN = 0
INFANTS = 0


def main():
    print("=== NIRA / ATA Availability Test ===")

    # اطلاعات ورود را هنگام اجرا وارد کن
    username = input("NIRA Username: ").strip()
    password = getpass("NIRA Password: ")

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
        print("\nConnecting to ATA NIRA API...")

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
            print("\nResponse is not valid JSON:")
            print(response.text[:3000])
            return

        print("\nAPI Response:")
        print(json.dumps(data, ensure_ascii=False, indent=2))

        flights = data.get("AvailableFlights", [])

        if flights:
            print(f"\nFound {len(flights)} flight(s):")

            for index, flight in enumerate(flights, start=1):
                print(f"\n--- Flight {index} ---")
                print("Airline:", flight.get("Airline"))
                print("Flight No:", flight.get("FlightNo"))
                print("Origin:", flight.get("Origin"))
                print("Destination:", flight.get("Destination"))
                print("Departure:", flight.get("DepartureDateTime"))
                print("Arrival:", flight.get("ArrivalDateTime"))
                print("Classes:", flight.get("ClassesStatus"))
                print("Prices:", flight.get("AdultTotalPrices"))

        else:
            print("\nNo flights found, or API returned an error.")
            print("Check the response above.")

    except requests.exceptions.Timeout:
        print("ERROR: API request timed out.")

    except requests.exceptions.HTTPError as error:
        print("HTTP ERROR:", error)
        print(response.text[:2000])

    except requests.exceptions.RequestException as error:
        print("CONNECTION ERROR:", error)


if __name__ == "__main__":
    main()
