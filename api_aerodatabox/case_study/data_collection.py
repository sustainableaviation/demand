import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import time

# Function to generate time intervals
def generate_time_intervals(start_date, end_date, delta):
    current = start_date
    while current < end_date:
        yield current, current + delta
        current += delta

# Airports list
airports = ["OEJN", "OERK"]

# API details
base_url = "https://aerodatabox.p.rapidapi.com/flights/airports/icao/{airport}/{start}/{end}"
querystring = {
    "withLeg": "false",
    "direction": "Departure",
    "withCancelled": "false",
    "withCodeshared": "false",
    "withCargo": "false",
    "withPrivate": "false",
    "withLocation": "false"
}
headers = {
    "X-RapidAPI-Key": "c07e00441amsh554a1379c06b08ep14e438jsnf5d2fca5cd7e",
    "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}

# Time interval settings
start_date = datetime(2023, 6, 13)
end_date = datetime(2023, 7, 13)
time_interval = timedelta(hours=12)

# Create output directory if it doesn't exist
output_dir = Path("airport_data")
output_dir.mkdir(exist_ok=True)

# Fetch and store data
for airport in airports:
    data = []
    for start, end in generate_time_intervals(start_date, end_date, time_interval):
        start_str = start.strftime("%Y-%m-%dT%H:%M")
        end_str = end.strftime("%Y-%m-%dT%H:%M")
        url = base_url.format(airport=airport, start=start_str, end=end_str)
        
        # Print the current API call
        print(f"Making API call for {airport} from {start_str} to {end_str}")
        
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            try:
                json_data = response.json()
                if "departures" in json_data:
                    for departure in json_data["departures"]:
                        filtered_data = {
                            "movement": {
                                "airport": departure.get("movement", {}).get("airport", "N/A"),
                                "scheduledTime": departure.get("movement", {}).get("scheduledTime", "N/A")
                            },
                            "aircraft": departure.get("aircraft", "N/A"),
                            "airline": departure.get("airline", "N/A")
                        }
                        data.append(filtered_data)
                else:
                    print(f"No departures data for {airport} from {start_str} to {end_str}")
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for {airport} from {start_str} to {end_str}")
        else:
            print(f"Failed to fetch data for {airport} from {start_str} to {end_str}: {response.status_code}")

        # Wait for 0.5 seconds before making the next request
        time.sleep(0.5)

    # Save data to JSON file
    output_file = output_dir / f"{airport}.json"
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

print("Data fetching complete.")
