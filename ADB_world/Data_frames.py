# IMPORTS #############################
#######################################

import json
import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import LineString


# load data############################
#######################################

# Get the current directory
current_directory = os.path.dirname(os.path.realpath(__file__))

# Read healtcheck file to get all airports with informations
file_path = os.path.join(current_directory, "Airport Data/Airports.json")
with open(file_path, 'r') as f:
    airports_icao = json.load(f)


# adjust data #########################
#######################################

# Extract icao names of airports from airports_icao and create a DataFrame
airport_list = [{'icao': airport_loc} for airport_loc in airports_icao['items']]
airport_list_df = pd.DataFrame(airport_list)

# Create a new DataFrame to store 'icao', 'airport_name', lat', and 'lon' of each airport
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
    airport_info_list.append(airport)  # appends it to list
airports_info_df = pd.DataFrame(airport_info_list)

# Create a new GeoDataFrame to store 'icao', 'airport_name', 'lat', and 'lon', 'geometry', of each airport (only needed if plotting is done using Geopanda)
departure_airports_geodf = gpd.GeoDataFrame(
        airports_info_df,
        geometry=gpd.points_from_xy(
            x=airports_info_df["lon"],
            y=airports_info_df["lat"],
            # Specify the coordinate reference system (standard for lat/lon)
            crs='EPSG:4326'
        )
    )


# create one big dataframe ############
#######################################

# Initialize a list to hold all data frames
all_connections = []

# Iterate over the different departure locations
for icao_departure in departure_airports_geodf['icao']:
    # Read JSON file with departure information for each airport
    file_path = os.path.join(current_directory, f"Airport Data/02-February/{icao_departure}.json")
    with open(file_path, 'r') as f:
        airport_connections = json.load(f)

    # Extract informations: arrival airport
    connections = []  # creates empty list to store the different connections
    for route in airport_connections['routes']:
        icao = route['destination'].get('icao')  # takes icao as an element -> returns None if no icao indicated (only very limited cases)
        if icao is not None:
            destination_info = route['destination'].get('location')
            # checks if destination airport has any location informations
            if destination_info is not None:
                lat = destination_info.get('lat')
                lon = destination_info.get('lon')
                # checks if destination has lat/lon of airport
                if lat is not None and lon is not None:
                    # safe departue and destination location as 2 different points
                    departure_point = (departure_airports_geodf.loc[departure_airports_geodf['icao'] == icao_departure, 'lon'].iloc[0],
                                       departure_airports_geodf.loc[departure_airports_geodf['icao'] == icao_departure, 'lat'].iloc[0])
                    destination_point = (lon, lat)
                    # create a line string between departure & destination location
                    line_geometry = LineString([departure_point, destination_point])
                    # Convert LineString to WKT (Well-Known Text) format so that it can be saved in a json format
                    line_wkt = line_geometry.wkt
                    # Add all information to the connections list
                    route_info = {
                        'icao_departure': icao_departure,
                        'departure_airport_name': departure_airports_geodf.loc[departure_airports_geodf['icao'] == icao_departure, 'airport_name'].iloc[0],
                        'icao_destination': icao,
                        'lat_departure': departure_airports_geodf.loc[departure_airports_geodf['icao'] == icao_departure, 'lat'].iloc[0],
                        'lon_departure': departure_airports_geodf.loc[departure_airports_geodf['icao'] == icao_departure, 'lon'].iloc[0],
                        'lat_destination': lat,
                        'lon_destination': lon,
                        'averageDailyFlights': route['averageDailyFlights'],
                        'line_geometry': line_wkt
                    }
                    connections.append(route_info)  # appends it to list

    # Create DataFrame containing all connections
    airport_connections_df = pd.DataFrame(connections)

    # Convert DataFrame to dictionary and append it to the connections
    all_connections.append(airport_connections_df.to_dict(orient='records'))


# Export as json ############
#############################

# Save all data frames as a single JSON file
output_json_path = os.path.join(current_directory, "Airport Data/flight_connections.json")
with open(output_json_path, 'w') as f:
    json.dump(all_connections, f, indent=4)

print(f"All data frames saved to {output_json_path}")
