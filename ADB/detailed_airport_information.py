import requests
import toml
import json
import time
from pathlib import Path

# Define paths
current_directory = Path(__file__).resolve().parent
config_path = current_directory / "API_Key/config.toml"


def get_api_key():
    try:
        with open(config_path, "r") as config_file:
            config = toml.load(config_file)
            return config["api"]["key"]
    except FileNotFoundError:
        print("Config file not found!")
        return None
    except KeyError:
        print("API key not found in config file!")
        return None

api_key = get_api_key()

if api_key is None:
    print("Exiting program due to missing API key.")
    exit()

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}

# Define the airports_info directory
airports_info_directory = current_directory / "airport_data/airports_detail_data"

# Check if the airports_info directory already exists
if airports_info_directory.exists():
    print(f"The directory 'airports_detail_data' already exists at {airports_info_directory}. Exiting program.")
    exit()

# Create the airports_info directory since it does not exist
airports_info_directory.mkdir(parents=True)

# Read the JSON file containing ICAO codes
json_file_path = current_directory / "airport_data/available_airports.json"
with open(json_file_path, 'r') as f:
    airports_icao = json.load(f)

# Fetch data from the API and write to JSON files
for icao in airports_icao['items']:
    url = f"https://aerodatabox.p.rapidapi.com/airports/icao/{icao}"
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        file_path = os.path.join(airports_info_directory, f"{icao}.json")

        # Write the JSON response to a file
        with open(file_path, "w") as file:
            file.write(response.text)
        print("JSON data saved to:", file_path)
    else:
        print("Failed to retrieve data from the API:", response.status_code)

    # Delay for 0.6 seconds to avoid hitting the rate limit
    time.sleep(0.6)
