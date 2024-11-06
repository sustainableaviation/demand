#######################################
# IMPORTS #############################
#######################################

import sys
from pathlib import Path
import json
import pandas as pd
import plotly.graph_objects as go
from matplotlib import cm
import numpy as np


#######################################
# PATHS ###############################
#######################################


current_directory = Path(__file__).resolve().parent
country_coord = current_directory / "data" / "country-coord.csv"
country_codes = current_directory / "data" / "CountryCodes.json"

api_aerodatabox_path = current_directory.parents[0] / 'api_aerodatabox'
sys.path.insert(0, str(api_aerodatabox_path))

# Local imports
from data_transformation_pandas import process_flight_connections


#######################################
# Create world map ####################
#######################################


# Create the blank world map
comparison_map = go.Figure(data=go.Choropleth(
    locations=[],  # No data for countries
    z=[],  # No data for color scale
))

# Update the layout for the map
comparison_map.update_layout(
    geo=dict(
        showframe=True,
        showcoastlines=True, coastlinecolor="lightgrey",
        showland=True, landcolor="black",
        showocean=True, oceancolor="dimgrey",
        showlakes=True, lakecolor="black",
        showcountries=True, countrycolor="lightgrey",
    ),

    margin=dict(l=5, r=5, t=5, b=5),
    legend=dict(
        y=0,  # Position the legend below the map
        x=0.5,
        xanchor='center',
        yanchor='top'
    ),
)


#######################################
# Data preparation ####################
#######################################


# get all connections as DataFrame and drop not needed colums
flight_data_df, x = process_flight_connections("Year")
flight_data_dropped_df = flight_data_df.drop(columns=['departure_country', 'lat_departure', 'lon_departure', 'lat_destination', 'lon_destination', 'departure_airport_name', 'departure_continent'])

# Load the country codes from JSON file
with open(country_codes, 'r') as file:
    country_codes = json.load(file)

# Load the coordinates of all countries into df
country_coord_df = pd.read_csv(country_coord)

# Add country codes for departure and destination to flight_data_dropped_df
for index, row in flight_data_dropped_df.iterrows():
    departure_code = row['icao_departure']
    destination_code = row['icao_destination']

    # Determine country code for departure airport
    if departure_code.startswith('K'):
        country_code_departure = "USA"
    else:
        first_two_letters_departure = departure_code[:2]
        country_code_departure = country_codes.get(first_two_letters_departure, 'ZZZZ')

    # Determine country code for destination airport
    if destination_code.startswith('K'):
        country_code_destination = "USA"
    else:
        first_two_letters_destination = destination_code[:2]
        country_code_destination = country_codes.get(first_two_letters_destination, 'ZZZZ')

    # Assign the country codes to new columns in the DataFrame
    flight_data_dropped_df.at[index, 'country_code_departure'] = country_code_departure
    flight_data_dropped_df.at[index, 'country_code_destination'] = country_code_destination

# Group by 'country_code_departure' and 'country_code_destination' and sum the 'averageDailyFlights'
combined_flights = flight_data_dropped_df.groupby(['country_code_departure', 'country_code_destination'], as_index=False).agg({'averageDailyFlights': 'sum'})

# Rename Departure_airport column inorder to combine it with coordinates of countires
combined_flights.columns = ["Alpha-3 code", "country_code_destination", "Total Departing Flights"]

# Merge with the coordinates DataFrame (df) on 'Alpha-3 code' and drop not needed columns
country_map_grouped_df = pd.merge(combined_flights, country_coord_df, on='Alpha-3 code', how='left')
country_map_grouped_df = country_map_grouped_df.drop(columns=['Alpha-2 code', "Numeric code"])

# Rename Destination_airport column inorder to combine it with coordinates of countires
country_map_grouped_df.columns = ["country_code_departure", "Alpha-3 code", "Total Departing Flights", "departure_country", "lat_departure", "lon_departure"]

# Merge with the coordinates DataFrame (df) on 'Alpha-3 code' and drop not needed columns
country_map_grouped_df = pd.merge(country_map_grouped_df, country_coord_df, on='Alpha-3 code', how='left')
country_map_grouped_df = country_map_grouped_df.drop(columns=['Country', 'Alpha-2 code', "Numeric code"])

# Rename all columns for clearity, and round 'total departing flights' to 2 decimal numbers
country_map_grouped_df.columns = ["country_code_departure", "country_code_destination", "Total Departing Flights", "departure_country", "lat_departure", "lon_departure", "lat_destination", "lon_destination"]
country_map_grouped_df["Total Departing Flights"] = country_map_grouped_df["Total Departing Flights"].apply(lambda x: round(x, 2))


#######################################
# Functions ###########################
#######################################

# Function to clear existing points on the map
def clear_map(fig):
    while fig.data:
        fig.data = []


# Function to create random colors
def generate_color_palette(n, colormap='tab20'):
    # Get the colormap
    colors = cm.get_cmap(colormap, n)

    # Generate RGB strings
    color_palette = []
    for i in range(n):
        rgba_color = colors(i)  # Get color in RGBA format
        rgb_color = 'rgb({}, {}, {})'.format(int(rgba_color[0] * 255),
                                             int(rgba_color[1] * 255),
                                             int(rgba_color[2] * 255))
        color_palette.append(rgb_color)

    return color_palette


# Function to create list with all departure countries
def get_unique_departure_countires():
    global country_map_grouped_df
    return country_map_grouped_df['departure_country'].unique().tolist()


# Function to create df which assigns to every country a color and saves it as a df
def get_colors_for_airports(list):
    
    color_palette = generate_color_palette(len(list))

    # Create a DataFrame mapping departure country to color
    color_map_df = pd.DataFrame({
        'departure_country': list,
        'color': color_palette
    })
    return color_map_df


#######################################
# Function for plotting ###############
#######################################


# create df with countries and corresponding colors
color_map_df = get_colors_for_airports(get_unique_departure_countires())


# function for plotting
def add_flight_routes(departure_country):
    global comparison_map, country_map_grouped_df, color_map_df

    clear_map(comparison_map)

    # Filter the DataFrame for the specified departure country and reset index
    filtered_df = country_map_grouped_df[(country_map_grouped_df['departure_country'] == departure_country)]
    filtered_df = filtered_df.reset_index()

    # Define logarithmic scaling parameters
    max_size = 70
    min_size = 0.5
    log_base = 10  # Adjust base as needed

    # Apply logarithmic scaling to 'Total Departing Flights'
    scaled_sizes = (np.log(filtered_df['Total Departing Flights'] + 1) / np.log(log_base))  # Adding 1 to avoid log(0)

    # Normalize size to range [min_size, max_size]
    scaled_sizes = ((scaled_sizes - scaled_sizes.min()) /
                    (scaled_sizes.max() - scaled_sizes.min()) *
                    (max_size - min_size)) + min_size

    # Separate lists to store traces for domestic flights and other flights
    traces_domestic = []
    traces_other = []

    for i in range(len(filtered_df)):
        departure_country = filtered_df.loc[i, 'departure_country']
        # get right color for plotting lines and markers
        color = color_map_df.loc[color_map_df['departure_country'] == departure_country, 'color'].values[0]

        # Plot a Red marker for domestic flights
        if filtered_df.loc[i, 'country_code_departure'] == filtered_df.loc[i, 'country_code_destination']:
            trace = go.Scattergeo(
                lon=[filtered_df.loc[i, 'lon_departure']],
                lat=[filtered_df.loc[i, 'lat_departure']],
                mode='markers',
                marker=dict(
                    size=scaled_sizes[i],  # Set marker size based on 'Total Departing Flights'
                    color='Red',  # Marker color for domestic flights
                    opacity=0.7,
                    line=dict(color='black', width=1)
                ),
                hoverinfo='text',
                text=f"Number of Domestic flights in {departure_country}: {filtered_df.loc[i, 'Total Departing Flights']}",
                showlegend=False,
            )
            traces_domestic.append(trace)

        else:
            # Plot line connecting departure and destination country
            trace_line = go.Scattergeo(
                lon=[filtered_df.loc[i, 'lon_departure'], filtered_df.loc[i, 'lon_destination']],
                lat=[filtered_df.loc[i, 'lat_departure'], filtered_df.loc[i, 'lat_destination']],
                mode='lines',
                line=dict(
                    width=scaled_sizes[i] / 7,  # Set line width based on 'Total Departing Flights'
                    color=color,  # Use dynamically fetched color
                ),
                hoverinfo='skip',
                opacity=0.8,
                showlegend=False,
            )
            traces_other.append(trace_line)

            # Plot destination country as a marker with scaled size
            trace_marker = go.Scattergeo(
                lon=[filtered_df.loc[i, 'lon_destination']],
                lat=[filtered_df.loc[i, 'lat_destination']],
                mode='markers',
                marker=dict(
                    size=scaled_sizes[i],  # Set marker size based on 'Total Departing Flights'
                    color=color,  # Use dynamically fetched color
                    opacity=0.7,
                    line=dict(color='black', width=1),
                ),
                hoverinfo='text',
                text=f"Country: {filtered_df.loc[i, 'country_code_destination']}<br>"
                     f"Total Departing Flights from {departure_country} to {filtered_df.loc[i, 'country_code_destination']} : {filtered_df.loc[i, 'Total Departing Flights']}",
                showlegend=False,
            )
            traces_other.append(trace_marker)

    # Add all traces for domestic flights first, followed by other flights
    for trace in traces_other:
        comparison_map.add_trace(trace)
    for trace in traces_domestic:
        comparison_map.add_trace(trace)
