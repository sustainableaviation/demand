import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

load_dotenv()
api_key = os.getenv('ADB_KEY')

# Function to retrieve data from the API for a given airport ICAO code and date
def get_airport_data(icao_code, date):
    url = f"https://aerodatabox.p.rapidapi.com/airports/icao/{icao_code}/stats/routes/daily/{date}"
    headers = {
        f"X-RapidAPI-Key": "{api_key}",
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

# Function to create folder for each month if it doesn't exist
def create_month_folder(month):
    folder_name = month.strftime("%m-%B")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

# Read the airport ICAO codes from the "Airports.json" file
with open("Airports.json", "r") as airports_file:
    airports_data = json.load(airports_file)

# Start from May 2023
current_date = datetime(2023, 5, 7)
end_date = datetime(2024, 5, 7)
while current_date <= end_date:
    # Create folder for the current month
    folder_name = create_month_folder(current_date)
    
    # Retrieve data for all airports for the current date
    date_str = current_date.strftime("%Y-%m-%d")
    print(f"Retrieving data for {date_str}...")
    for airport_icao in airports_data["items"]:
        airport_data = get_airport_data(airport_icao, date_str)
        if airport_data:
            # Save the data to a file named after the airport ICAO code within the month folder
            file_path = os.path.join(folder_name, f"{airport_icao}.json")
            with open(file_path, "w") as json_file:
                json.dump(airport_data, json_file)
            print(f"Data for airport {airport_icao} saved successfully.")
        else:
            print(f"Failed to retrieve data for airport {airport_icao}.")

    # Move to the next month
    current_date += relativedelta(months=1)
    current_date = current_date.replace(day=7)  # Set the day to the 7th day of the next month
