#######################################
# IMPORTS #############################
#######################################


import pandas as pd
import sys
from pathlib import Path


#######################################
# PATHS ###############################
#######################################

# Ensure the correct module path is added
current_directory = Path(__file__).resolve().parent
api_aerodatabox_path = current_directory.parents[0] / 'api_aerodatabox'
sys.path.insert(0, str(api_aerodatabox_path))

import data_transformation_pandas


#######################################
# Data preparation ####################
#######################################


# Process flight connections to get DataFrame
flight_data_df, daily_flights_df = data_transformation_pandas.process_flight_connections("Year")

# Initialize total_flights counter and calculate number of flights
number_of_flights = daily_flights_df['number_of_total_flights'].sum()

# Calculate number of connections and airports
number_of_connections = len(flight_data_df)
number_of_airports = len(daily_flights_df)

# Create data dictionary without decimal places
data = {
    "label": ["number_of_airports", "number_of_connections", "number_of_flights"],
    "numbers": [int(number_of_airports), int(number_of_connections), int(number_of_flights)],
}

# Create DataFrame
General_numbers_df = pd.DataFrame(data)

# Sort daily_flights_df by number_of_total_flights in descending order and select top 25 airports
top_25_airports_df = daily_flights_df.sort_values(by='number_of_total_flights', ascending=False).head(25)
top_25_airports_df.reset_index(drop=True, inplace=True)

# Rename columns as per your requirement
top_25_airports_df = top_25_airports_df.rename(columns={
    "icao_departure": "ICAO Code",
    "departure_airport_name": "Airport Name",
    "number_of_total_flights": "Average Daily Departing Flights"
})[["ICAO Code", "Airport Name", "Average Daily Departing Flights"]]  # Select specific columns

# Add a column counting from 1 to 25
top_25_airports_df.insert(0, "Rank", range(1, 26))

# Format numbers in Total Flights column to 2 decimal places
top_25_airports_df["Average Daily Departing Flights"] = top_25_airports_df["Average Daily Departing Flights"].apply(lambda x: round(x, 2))


# Function to create a unique key for each pair (order-independent)
def create_pair_key(row):
    return tuple(sorted([row["Departure Airport"], row["Destination Airport"]]))


# Rename columns
flight_data_df = flight_data_df.rename(columns={
    "departure_airport_name": "Departure Airport",
    "destination_airport_name": "Destination Airport",
    "averageDailyFlights": "Average Daily Flights",
})

# Create a pair key for each row
flight_data_df["pair_key"] = flight_data_df.apply(create_pair_key, axis=1)

# Group by the pair key and sum the average daily flights
grouped_df = flight_data_df.groupby("pair_key", as_index=False).agg({
    "Departure Airport": "first",
    "Destination Airport": "first",
    "Average Daily Flights": "sum"
})

# Sort by the summed average daily flights and select top 25 connections
top_25_connections_df = grouped_df.sort_values(by="Average Daily Flights", ascending=False).head(25)

# Format numbers in Average Daily Flights column to 2 decimal places
top_25_connections_df["Average Daily Flights"] = top_25_connections_df["Average Daily Flights"].apply(lambda x: round(x, 2))

# Add a column counting from 1 to 25
top_25_connections_df.insert(0, "Rank", range(1, 26))
top_25_connections_df = top_25_connections_df.drop(columns=["pair_key"])
