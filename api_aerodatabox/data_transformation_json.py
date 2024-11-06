#######################################
# IMPORTS #############################
#######################################

import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
from pathlib import Path


#######################################
# Function to prepare airport data
#######################################

"""
    This function reads a list with all airports with available data from the
    available_airports.json, extracts detailed information for each of those
    single airports from their respective JSON files, and compiles the data
    into a GeoDataFrame.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing information about
                          the airports, including ICAO code, name, latitude,
                          longitude, and geometry. Returns None if there is
                          an error in reading the JSON data.


    Each airport_data/airports_detail_data/{ICAO_CODE}.json file contains the
    detailed information for the corresponding airport.

    Example JSON Structure:

        available_airports.json:
        {
            "items": ["ICAO1", "ICAO2", "ICAO3"]
        }

        {ICAO_CODE}.json:
        {
            "icao":	    "CYWK"
            "fullName": "Airport Name",
            "location": {
                "lat": 12.34,
                "lon": 56.78
            }
        }

        The function will return a DataFrame of the form:
    +--------------+-----------+-------------------------+----------+------------+------+-----------+
    | UID (=index) | icao      | airport_name            | lat      | lon        | geometry         |
    +==============+===========+=========================+==========+============+==================+
    | 123          | CYWK      | Wabush                  | 52.9219  | -66.8644   | -66.8644 52.9219 |
    +--------------+-----------+-------------------------+----------+------------+------+------------
    | 456          | LEST      | Santiago de Compostela  | 42.8963  | -8.41514   | -8.41514 42.8963 |
    +--------------+-----------+-------------------------+----------+------------+------+------------
    """


def prepare_airport_data():
    current_directory = Path(__file__).resolve().parent

    # Read airports data
    file_path = current_directory / "airport_data/available_airports.json"
    try:
        with open(file_path, 'r') as f:
            airports_icao = json.load(f)
    except json.decoder.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}: {e}")
        return None

    # Extract airport information
    airport_list = [{'icao': airport_loc} for airport_loc in airports_icao['items']]
    airport_list_df = pd.DataFrame(airport_list)

    # Create airport DataFrame
    airport_info_list = []
    for icao_airport in airport_list_df['icao']:
        file_path = current_directory / f"airport_data/airports_detail_data/{icao_airport}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                airport_info = json.load(f)
            airport = {
                'icao': icao_airport,
                'airport_name': airport_info['fullName'],
                'lat': airport_info['location']['lat'],
                'lon': airport_info['location']['lon'],
                'country': airport_info['country']['name'],
                'country_code': airport_info['country']['code'],
                'continent': airport_info['continent']['name'],
            }
            airport_info_list.append(airport)
        else:
            print(f"Data for {icao_airport} not found. Skipping...")
    airports_info_df = pd.DataFrame(airport_info_list)

    # Create GeoDataFrame
    departure_airports_geodf = gpd.GeoDataFrame(
        airports_info_df,
        geometry=gpd.points_from_xy(
            x=airports_info_df["lon"],
            y=airports_info_df["lat"],
            crs='EPSG:4326'
        )
    )
    return departure_airports_geodf


#######################################
# Function to generate flight connections JSON
#######################################

"""
    Generates a JSON files containing flight connection data for a given month.

    This function reads flight connection data for a specified month and a
    defined number of departure airports, processes the data to extract
    relevant information, and saves the flight connection details as
    JSON files.

    Args:
        month (str): The month for which flight connection data is to be generated.
        departure_airports_geodf (gpd.GeoDataFrame): GeoDataFrame containing information
                                                     about the departure airports, including
                                                     ICAO codes, names, latitudes, longitudes,
                                                     and geometries.
        x (int, optional): The number of departure airports to process. Defaults to 100.

    Returns:
        None

    Each connection_data/{month}/{ICAO_CODE}.json file should contain the
    flight connection details for the corresponding departure airport and month.

    Example JSON Structure:

        {ICAO_CODE}.json:
        {
            "routes": [
                {
                    "destination": {
                        "icao": "DEST_ICAO",
                        "location": {
                            "lat": 12.34,
                            "lon": 56.78
                        }
                    },
                    "averageDailyFlights": 5.5
                }
            ]
        }

    The function will process these files and generate a JSON file of the form:

    flight_connections_{month}.json:
    [
        {
            "icao_departure": "DEP_ICAO",
            "departure_airport_name": "Departure Airport Name",
            "icao_destination": "DEST_ICAO",
            "lat_departure": 12.34,
            "lon_departure": 56.78,
            "lat_destination": 12.34,
            "lon_destination": 56.78,
            "averageDailyFlights": 5.5,
            "line_geometry": "LINESTRING (lon1 lat1, lon2 lat2)"
        },
        ...
    ]

    """


def generate_flight_connections_json(month, departure_airports_geodf, x=100):
    current_directory = Path(__file__).resolve().parent

    # Initialize a list to hold all data frames
    all_connections = []

    # Iterate over the different departure locations
    for icao_departure in departure_airports_geodf['icao'][:x]:
        file_path = current_directory / f"connection_data/{month}/{icao_departure}.json"
        try:
            with open(file_path, 'r') as f:
                airport_connections = json.load(f)
        except FileNotFoundError:
            print(f"Warning: JSON file for {icao_departure} during {month} not found. Skipping this airport.")
            continue

        connections = []
        for route in airport_connections['routes']:
            icao = route['destination'].get('icao')
            if icao is not None:
                destination_info = route['destination'].get('location')
                if destination_info is not None:
                    lat = destination_info.get('lat')
                    lon = destination_info.get('lon')
                    if lat is not None and lon is not None:
                        departure_point = (
                            departure_airports_geodf.loc[departure_airports_geodf['icao'] == icao_departure, 'lon'].iloc[0],
                            departure_airports_geodf.loc[departure_airports_geodf['icao'] == icao_departure, 'lat'].iloc[0]
                        )
                        destination_point = (lon, lat)
                        line_geometry = LineString([departure_point, destination_point])
                        line_wkt = line_geometry.wkt
                        route_info = {
                            'icao_departure': icao_departure,
                            'departure_airport_name': departure_airports_geodf.loc[
                                departure_airports_geodf['icao'] == icao_departure, 'airport_name'].iloc[0],
                            'departure_country': departure_airports_geodf.loc[
                                departure_airports_geodf['icao'] == icao_departure, 'country'].iloc[0],
                            'departure_continent': departure_airports_geodf.loc[
                                departure_airports_geodf['icao'] == icao_departure, 'continent'].iloc[0],
                            'icao_destination': icao,
                            'destination_airport_name': route['destination']['name'],
                            'destination_country_code': route['destination']['countryCode'],
                            'lat_departure': departure_airports_geodf.loc[
                                departure_airports_geodf['icao'] == icao_departure, 'lat'].iloc[0],
                            'lon_departure': departure_airports_geodf.loc[
                                departure_airports_geodf['icao'] == icao_departure, 'lon'].iloc[0],
                            'lat_destination': lat,
                            'lon_destination': lon,
                            'averageDailyFlights': route['averageDailyFlights'],
                            'line_geometry': line_wkt
                        }
                        connections.append(route_info)

        # Create DataFrame containing all connections
        airport_connections_df = pd.DataFrame(connections)

        # Convert DataFrame to dictionary and append it to the connections
        all_connections.append(airport_connections_df.to_dict(orient='records'))

    # Save data frames as individual JSON files
    # Save all connections as a single JSON file
    output_json_path = current_directory / f"connection_data/flight_connections_{month}.json"
    with open(output_json_path, 'w') as f:
        json.dump(all_connections, f, indent=4)
    print(f"All connections for {month} saved to {output_json_path}")


#######################################
# create the different JSON files
#######################################

departure_airports_geodf = prepare_airport_data()
month_list = ["01-January", "02-February", "03-March", "04-April", "05-May", "06-June", "07-July", "08-August",
              "09-September", "10-October", "11-November", "12-December"]

# File path for storing flight connection data
current_directory = Path(__file__).resolve().parent

# Set a flag to indicate if any connection files are missing
all_connections_exist = True

# Iterate over month_list
for month in month_list:
    # File path for the current month's flight connections
    month_json_path = current_directory / f"connection_data/flight_connections_{month}.json"

    # If the file doesn't exist, generate and save flight connection data
    if not month_json_path.exists():
        all_connections_exist = False  # Set flag to False if any file is missing
        generate_flight_connections_json(month, departure_airports_geodf, 100)

# Print a message only if all connection files already exist
if all_connections_exist:
    print("All connection files already exist.")


# Prompt the user to decide whether to recreate the flight connection files or not
user_response = input("Do you want to recreate the flight connection files? (yes/no): ").lower()

while True:
    try:
        number_of_airports = int(input(f"For how many airports do you want to create the connections (max {len(departure_airports_geodf)}): "))
        if number_of_airports > len(departure_airports_geodf):
            print("Please enter a number smaller than or equal to the number of max airports.")
        else:
            break  # Exit the loop if the entered number is valid
    except ValueError:
        print("Please enter a valid integer.")

# If the user chooses to recreate the files
if user_response == "yes":
    # Iterate over month_list
    for month in month_list:
        # File path for the current month's flight connections
        month_json_path = current_directory / f"connection_data/flight_connections_{month}.json"
        # Generate and save flight connection data
        generate_flight_connections_json(month, departure_airports_geodf, number_of_airports)

# If the user chooses not to recreate the files
elif user_response == "no":
    print("Flight connection files will not be recreated.")

# If the user provides an invalid response
else:
    print("Invalid response. Please enter 'yes' or 'no'.")
