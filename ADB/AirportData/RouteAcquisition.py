import os
import requests
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import toml


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


def get_airport_routes(icao_code, date):
    url = f"https://aerodatabox.p.rapidapi.com/airports/icao/{icao_code}/stats/routes/daily({date})"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None


def create_month_folder(month):
    folder_name = month.strftime("%m-%B")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

""" Read the airport ICAO codes from the "Airports.json" file
This function requires a file called Airports.json from the Healthcheck.py
"""
with open("Airports.json", "r") as airports_file:
    airports_dataset = json.load(airports_file)

start_date = datetime(year=2023, month=5, day=7)
end_date = datetime(year=2024, month=5, day=7)
while start_date <= end_date:
    folder_name = create_month_folder(start_date)
    date_str = start_date.strftime("%Y-%m-%d")
    print(f"Retrieving data for {date_str}...")
    for airport_icao in airports_dataset["items"]:
        airport_routes = get_airport_routes(airport_icao, date_str)
        if airport_routes:
            file_path = os.path.join(folder_name, f"{airport_icao}.json")
            with open(file_path, "w") as json_file:
                json.dump(airport_routes, json_file)
            print(f"Data for airport {airport_icao} saved successfully.")
        else:
            print(f"Failed to retrieve data for airport {airport_icao}.")
    start_date += relativedelta(months=1)
    start_date = start_date.replace(day=7)
