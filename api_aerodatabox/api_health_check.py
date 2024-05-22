import requests
from pathlib import Path

# Determine the current directory
current_directory = Path(__file__).resolve().parent

# Now you can import the module
import api_utlitities
headers = api_utlitities.headers

url = "https://aerodatabox.p.rapidapi.com/health/services/feeds/FlightSchedules/airports"

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
