#######################################
# IMPORTS #############################
#######################################

import json
import pandas as pd
from pathlib import Path

#######################################
# create 2 panda Data frames ##########
#######################################

"""
    This function reads flight connection data from a JSON file for the
    specified month,processes the data to extract relevant information
    about flight connections,and generates two pandas DataFrames:
    one with detailed connection data and another with the total number of
    daily flights per departure airport.

    Args:
        month (str): The month for which flight connection data is to be processed.

    Returns:
        tuple: A tuple containing two pandas DataFrames:
            - flight_data_df (pd.DataFrame): DataFrame containing detailed flight connection data,
                                              including latitude and longitude of departure and
                                              destination airports, ICAO codes, and average daily flights.
            - daily_flights_df (pd.DataFrame): DataFrame containing the total number of daily flights
                                               per departure airport, including ICAO codes, airport names,
                                               latitudes, and longitudes.

    Example JSON Structure:

        flight_connections_{month}.json:
        [
            [
                {
                    "icao_departure": "DEP_ICAO",
                    "departure_airport_name": "Departure Airport Name",
                    "lat_departure": 12.34,
                    "lon_departure": 56.78,
                    "icao_destination": "DEST_ICAO",
                    "lat_destination": 12.34,
                    "lon_destination": 56.78,
                    "averageDailyFlights": 5.5
                },
                ...
            ],
            ...
        ]

    The function will process these files and generate the following DataFrames:

    flight_data_df:
    +--------------+---------------+---------------+-----------------+-----------------+----------------+------------------------+------------------+---------------------|
    | UID (=index) | lat_departure | lon_departure | lat_destination | lon_destination | icao_departure | departure_airport_name | icao_destination | averageDailyFlights |
    +--------------+---------------+---------------+-----------------+-----------------+----------------+------------------------+------------------+---------------------+
    | 0            | 12.34         | 56.78         | 12.34           | 56.78           | DEP_ICAO       | Departure Airport      | DEST_ICAO        | 5.5                 |
    +--------------+---------------+---------------+-----------------+-----------------+----------------+------------------------+------------------+---------------------+

    daily_flights_df:
    +--------------+--------------------+------------------------+-------------------------+---------------+---------------+
    | UID (=index) | icao_departure     | departure_airport_name | number_of_total_flights | lat_departure | lon_departure |
    +--------------+--------------------+------------------------+-------------------------+---------------+---------------+
    | 0            | DEP_ICAO           | Departure Airport      | 100                     | 12.34         | 56.78         |
    +--------------+--------------------+------------------------+-------------------------+---------------+---------------+
    """


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
