import json
import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import LineString


def generate_flight_connections_json(month):
    # Get the current directory
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Read airports data
    file_path = os.path.join(current_directory, "Airport Data/Airports.json")
    try:
        with open(file_path, 'r') as f:
            airports_icao = json.load(f)
    except json.decoder.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}: {e}")
        return

    # Extract airport information
    airport_list = [{'icao': airport_loc} for airport_loc in airports_icao['items']]
    airport_list_df = pd.DataFrame(airport_list)

    # Create airport DataFrame
    airport_info_list = []
    for icao_airport in airport_list_df['icao']:
        file_path = os.path.join(current_directory, f"Airport Data/airports_info/{icao_airport}.json")
        with open(file_path, 'r') as f:
            airport_info = json.load(f)
        airport = {
            'icao': icao_airport,
            'airport_name': airport_info['fullName'],
            'lat': airport_info['location']['lat'],
            'lon': airport_info['location']['lon'],
        }
        airport_info_list.append(airport)
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

    # Initialize a list to hold all data frames
    all_connections = []

    # Iterate over the different departure locations
    for icao_departure in departure_airports_geodf['icao'][:50]:
        file_path = os.path.join(current_directory, f"Airport Data/{month}/{icao_departure}.json")
        with open(file_path, 'r') as f:
            airport_connections = json.load(f)

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
                            'icao_destination': icao,
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
    output_json_path = os.path.join(current_directory, f"Airport Data/flight_connections_{month}.json")
    with open(output_json_path, 'w') as f:
        json.dump(all_connections, f, indent=4)
    print(f"All connections saved to {output_json_path}")


def process_flight_connections(month):
    # Get the current directory
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Data import
    file_path = os.path.join(current_directory, f"Airport Data/flight_connections_{month}.json")
    with open(file_path, 'r') as f:
        connection_data = json.load(f)

    # Extract data
    data = [{
        'lat_departure': connection['lat_departure'],
        'lon_departure': connection['lon_departure'],
        'lat_destination': connection['lat_destination'],
        'lon_destination': connection['lon_destination'],
        'departure': connection['icao_departure'],
        'departure_name': connection['departure_airport_name'],
        'destination': connection['icao_destination'],
        'daily_flights': connection['averageDailyFlights']
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
        'departure_icao': departure_icao_list,
        'departure_name': departure_name_list,
        'number_of_total_flights': number_of_total_flights_list,
        'lat_departure': lat_departure_list,
        'lon_departure': lon_departure_list
    }
    daily_flights_df = pd.DataFrame(flight_data)

    return flight_data_df, daily_flights_df