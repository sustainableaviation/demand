# IMPORTS #############################
#######################################
import json
import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import LineString

current_directory = os.path.dirname(os.path.realpath(__file__))  # Get the current directory

# Read healtcheck file to get all airports with informations
file_path = os.path.join(current_directory, "Airport Data/Airports.json")
with open(file_path, 'r') as f:
    airports_icao = json.load(f)

# Extract icao names of airports and create a DataFrame
airport_list = [{'icao': airport_loc} for airport_loc in airports_icao['items']]
airports_df = pd.DataFrame(airport_list)

# Create a new DataFrame to store 'icao', 'lat', and 'lon'
new_airports = []
for location in airports_df['icao']:
    file_path = os.path.join(current_directory, f"Airport Data/airports_info/{location}.json")  # Define the file path
    with open(file_path, 'r') as f:
        airport_info = json.load(f)
    airport = {
            'icao': location,
            'lat': airport_info['location']['lat'],
            'lon': airport_info['location']['lon'],
        }
    new_airports.append(airport)  # appends it to list
new_airports_df = pd.DataFrame(new_airports)

# Create a new GeoDataFrame to store 'icao', 'lat', and 'lon', 'geometry'
airports_geodf = gpd.GeoDataFrame(
        new_airports_df,
        geometry=gpd.points_from_xy(
            x=new_airports_df["lon"],
            y=new_airports_df["lat"],
            # Specify the coordinate reference system (standard for lat/lon)
            crs='EPSG:4326'
        )
    )

# Initialize a list to hold all data frames
all_data_frames = []

# Iterate over the locations
for location in airports_geodf['icao']:
    # Read JSON file
    file_path = os.path.join(current_directory, f"Airport Data/05-May/{location}.json")
    with open(file_path, 'r') as f:
        airport_connections = json.load(f)

    # Extract desired fields
    connections = []  # creates empty list
    for route in airport_connections['routes']:
        icao = route['destination'].get('icao')  # takes icao as an element -> returns None if no icao indicated
        if icao is not None:
            location_info = route['destination'].get('location')
            if location_info is not None:
                lat = location_info.get('lat')
                lon = location_info.get('lon')
                if lat is not None and lon is not None:
                    departure_point = (airports_geodf.loc[airports_geodf['icao'] == location, 'lon'].iloc[0],
                                       airports_geodf.loc[airports_geodf['icao'] == location, 'lat'].iloc[0])
                    landing_point = (lon, lat)
                    line_geometry = LineString([departure_point, landing_point])
                    # Convert LineString to WKT (Well-Known Text) format
                    line_wkt = line_geometry.wkt
                    # Add route information to the connections list
                    route_info = {
                        'icao_departure': location,
                        'icao_landing': icao,
                        'lat_departure': airports_geodf.loc[airports_geodf['icao'] == location, 'lat'].iloc[0],
                        'lon_departure': airports_geodf.loc[airports_geodf['icao'] == location, 'lon'].iloc[0],
                        'lat_landing': lat,
                        'lon_landing': lon,
                        'averageDailyFlights': route['averageDailyFlights'],
                        'line_geometry': line_wkt  # Save WKT representation
                    }
                    connections.append(route_info)  # appends it to list

    # Create DataFrame
    airport_connections_df = pd.DataFrame(connections)

    # Convert DataFrame to dictionary and append to the list
    all_data_frames.append(airport_connections_df.to_dict(orient='records'))

# Save all data frames as a single JSON file
output_json_path = os.path.join(current_directory, "Airport Data/airport_connections.json")
with open(output_json_path, 'w') as f:
    json.dump(all_data_frames, f, indent=4)

print(f"All data frames saved to {output_json_path}")
