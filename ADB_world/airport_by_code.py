import os
import requests
import json
import time

headers = {
	"X-RapidAPI-Key": "59a275298cmsh24590c15cf01d92p12e3a3jsn0f5baacc5959",
	"X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}

# Read JSON file
with open('/Users/barend/Desktop/Thesis/demandmap/ADB_world/Airport Data/Airports.json', 'r') as f:
    airports_icao = json.load(f)

for icao in airports_icao['items']:
    url = f"https://aerodatabox.p.rapidapi.com/airports/icao/{icao}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200: # Check if the request was successful
        current_directory = os.path.dirname(os.path.realpath(__file__)) # Get the current directory
        file_path = os.path.join(current_directory, f"Airport Data/airports_info/{icao}.json") # Define the file path
        with open(file_path, "w") as file: # Write the JSON response to a file
            file.write(response.text)    
        print("JSON data saved to:", file_path)
    else:
        print("Failed to retrieve data from the API:", response.status_code)
        # Delay for 0.6 second to avoid hitting the rate limit of 120 calls per minute
    time.sleep(0.6)
