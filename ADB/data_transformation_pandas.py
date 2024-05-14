#######################################
# IMPORTS #############################
#######################################

import json
import pandas as pd
from pathlib import Path

#######################################
# create 2 panda Data frames ##########
#######################################

def process_flight_connections(month):
    # Get the current directory
    current_directory = Path(__file__).resolve().parent

    # Data import
    file_path = current_directory / f"connection_data/flight_connections_{month}.json"
    with open(file_path, 'r') as f:
        connection_data = json.load(f)

    # Extract data
    data = [{
        'lat_departure': connection['lat_departure'],
        'lon_departure': connection['lon_departure'],
        'lat_destination': connection['lat_destination'],
        'lon_destination': connection['lon_destination'],
        'icao_departure': connection['icao_departure'],
        'departure_airport_name': connection['departure_airport_name'],
        'icao_destination': connection['icao_destination'],
        'averageDailyFlights': connection['averageDailyFlights']
    } for departing_airport in connection_data for connection in departing_airport]

    # Create DataFrame with the connection data
    flight_data_df = pd.DataFrame(data)

    # Adjust data to get the number of daily_flights per airport
    departure_icao_list = []
    number_of_total_flights_list = []
    lat_departure_list = []
    lon_departure_list = []
    departure_name_list = []

    for connection_list in connection_data:
        flights_by_departure = {}

        for connection in connection_list:
            departure_icao = connection["icao_departure"]
            daily_flights = connection["averageDailyFlights"]
            departure_name = connection["departure_airport_name"]

            if departure_icao in flights_by_departure:
                flights_by_departure[departure_icao] += daily_flights
            else:
                flights_by_departure[departure_icao] = daily_flights

        for departure_icao, total_flights in flights_by_departure.items():
            departure_icao_list.append(departure_icao)
            number_of_total_flights_list.append(total_flights)
            departure_name_list.append(departure_name)

            for connection in connection_list:
                if connection["icao_departure"] == departure_icao:
                    lat_departure_list.append(connection["lat_departure"])
                    lon_departure_list.append(connection["lon_departure"])
                    break

    # Create DataFrame for daily flights
    flight_data = {
        'icao_departure': departure_icao_list,
        'departure_airport_name': departure_name_list,
        'number_of_total_flights': number_of_total_flights_list,
        'lat_departure': lat_departure_list,
        'lon_departure': lon_departure_list
    }
    daily_flights_df = pd.DataFrame(flight_data)

    return flight_data_df, daily_flights_df