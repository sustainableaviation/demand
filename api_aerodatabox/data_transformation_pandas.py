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
                    icao_departure:	"DAOR"
                    departure_airport_name:	"Béchar Boudghene Ben Ali Lotfi"
                    departure_country:	"Algeria"
                    departure_continent:	"Africa"
                    icao_destination:	"DAAG"
                    destination_airport_name:	"Algiers Houari Boumediene"
                    destination_country_code:	"DZ"
                    lat_departure:	31.6457
                    lon_departure:	-2.26986
                    lat_destination:	36.691
                    lon_destination:	3.215409
                    averageDailyFlights:	1.43
                    line_geometry:	"LINESTRING (-2.26986 31.6457, 3.215409 36.691)"
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

    # Initialize lists for daily flights per departure airport
    departure_icao_list = []
    number_of_total_flights_list = []
    lat_departure_list = []
    lon_departure_list = []
    departure_name_list = []
    departure_country_list = []
    departure_continent_list = []

    for connection_list in connection_data:
        flights_by_departure = {}

        for connection in connection_list:
            departure_icao = connection["icao_departure"]
            daily_flights = connection["averageDailyFlights"]
            departure_name = connection["departure_airport_name"]

            # Accumulate daily flights per departure airport
            if departure_icao in flights_by_departure:
                flights_by_departure[departure_icao] += daily_flights
            else:
                flights_by_departure[departure_icao] = daily_flights

        # Append data to lists
        for departure_icao, total_flights in flights_by_departure.items():
            departure_icao_list.append(departure_icao)
            number_of_total_flights_list.append(total_flights)
            # Find the corresponding coordinates and name for the departure airport
            for connection in connection_list:
                if connection["icao_departure"] == departure_icao:
                    departure_name_list.append(connection["departure_airport_name"])
                    lat_departure_list.append(connection["lat_departure"])
                    lon_departure_list.append(connection["lon_departure"])
                    departure_country_list.append(connection["departure_country"])
                    departure_continent_list.append(connection["departure_continent"])
                    break

    # Create DataFrame for daily flights
    flight_data = {
        'icao_departure': departure_icao_list,
        'departure_airport_name': departure_name_list,
        'departure_country': departure_country_list,
        'departure_continent': departure_continent_list,
        'number_of_total_flights': number_of_total_flights_list,
        'lat_departure': lat_departure_list,
        'lon_departure': lon_departure_list
    }
    daily_flights_df = pd.DataFrame(flight_data)

    # Create DataFrame with the connection data
    data = [{
        'lat_departure': connection['lat_departure'],
        'lon_departure': connection['lon_departure'],
        'lat_destination': connection['lat_destination'],
        'lon_destination': connection['lon_destination'],
        'icao_departure': connection['icao_departure'],
        'departure_airport_name': connection['departure_airport_name'],
        'departure_country': connection['departure_country'],
        'departure_continent': connection['departure_continent'],
        'icao_destination': connection['icao_destination'],
        'destination_airport_name': connection['destination_airport_name'],
        'averageDailyFlights': connection['averageDailyFlights']
    } for connection_list in connection_data for connection in connection_list]

    flight_data_df = pd.DataFrame(data)

    return flight_data_df, daily_flights_df
