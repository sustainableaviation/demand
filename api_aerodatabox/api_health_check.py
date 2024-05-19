import requests
import toml
from pathlib import Path


def get_api_key():
    try:
        with open("config.toml", "r") as config_file:
            config = toml.load(config_file)
            return config["api"]["key"]
    except FileNotFoundError:
        print("Config file not found!")
        return None
    except KeyError:
        print("API key not found in config file!")
        return None


api_key = get_api_key()

url = "https://aerodatabox.p.rapidapi.com/health/services/feeds/FlightSchedules/airports"

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:

    # Get the current directory
    file_path = current_directory / "airport_data/available_airports.json"

    # Write the JSON response to a file
    with open(file_path, "w") as file:
        file.write(response.text)

    print("JSON data saved to:", file_path)
else:
    print("Failed to retrieve data from the API:", response.status_code)
