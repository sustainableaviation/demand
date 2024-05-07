# IMPORTS #############################
#######################################

import plotly.graph_objects as go
import os
import json
import pandas as pd


# Get the current directory
current_directory = os.path.dirname(os.path.realpath(__file__))


# Data import #########################
#######################################

# Get connection data
file_path = os.path.join(current_directory, "Airport Data/flight_connections.json")
with open(file_path, 'r') as f:
    connection_data = json.load(f)

# Extract data from JSON file using list comprehensions
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

# Create a new DataFrame with the connection data
flight_data_df = pd.DataFrame(data)


# adjust data #########################
#######################################

# get the number of daily_flights per airport
# Initialize lists to hold aggregated data
departure_icao_list = []
number_of_total_flights_list = []
lat_departure_list = []
lon_departure_list = []
departure_name_list = []

# Iterate over the provided data
for connection_list in connection_data:
    # Initialize dictionaries to store flights and total daily flights for each departure airport
    flights_by_departure = {}
    total_flights_by_departure = {}

    # Iterate over each flight connection
    for connection in connection_list:
        departure_icao = connection["icao_departure"]
        daily_flights = connection["averageDailyFlights"]
        departure_name = connection["departure_airport_name"]

        # Sum up daily flights for each departure airport
        if departure_icao in flights_by_departure:
            flights_by_departure[departure_icao] += daily_flights
        else:
            flights_by_departure[departure_icao] = daily_flights

    # Iterate over flights by departure airport to create a list of aggregated data
    for departure_icao, total_flights in flights_by_departure.items():
        departure_icao_list.append(departure_icao)
        number_of_total_flights_list.append(total_flights)
        departure_name_list.append(departure_name)

        # Find the corresponding departure coordinates
        for connection in connection_list:
            if connection["icao_departure"] == departure_icao:
                lat_departure_list.append(connection["lat_departure"])
                lon_departure_list.append(connection["lon_departure"])
                break

# Create DataFrame
flight_data = {
    'departure_icao': departure_icao_list,
    'departure_name': departure_name_list,
    'number_of_total_flights': number_of_total_flights_list,
    'lat_departure': lat_departure_list,
    'lon_departure': lon_departure_list
}
daily_flights_df = pd.DataFrame(flight_data)
print(daily_flights_df)


# Calculate the maximum value of 'daily_flights' column
max_daily_flights = daily_flights_df['number_of_total_flights'].max()


# Plotting ############################
#######################################

# Define maximum and minimum sizes
max_size = 20
min_size = 2

# Logarithmically scale the values between min and max sizes -> maybe sigmoid function for scaling
scaled_sizes = ((daily_flights_df['number_of_total_flights'] - daily_flights_df['number_of_total_flights'].min()) /
                (daily_flights_df['number_of_total_flights'].max() - daily_flights_df['number_of_total_flights'].min()) *
                (max_size - min_size)) + min_size


# Plot the different airports
fig = go.Figure(go.Scattergeo(
    lat=daily_flights_df["lat_departure"],
    lon=daily_flights_df["lon_departure"],
    text=daily_flights_df["departure_name"] + '<br>'
        + "Number of average departing daily flights: "
        + daily_flights_df["number_of_total_flights"].apply(lambda x: round(x, 2)).astype(str),  # Round to 2 decimal places
    hoverinfo='text',  # Set hoverinfo to 'text'
    mode='markers',
    marker=dict(
        size=scaled_sizes,  # Scale the sizes between min and max sizes
        opacity=0.9,
        line_width=0,
        autocolorscale=False,
        colorscale='Bluered',
        cmin=0,
        color=daily_flights_df['number_of_total_flights'],
        cmax=max_daily_flights,  # Use the calculated maximum value
        colorbar_title="Average Daily<br>Departing Flights<br>May 2023"
    )
))


# Define maximum and minimum opacities
max_opacity = 1
min_opacity = 0.0

# Scale the opacities between min and max opacities
scaled_opacities = ((flight_data_df['daily_flights'] - flight_data_df['daily_flights'].min()) /
                    (flight_data_df['daily_flights'].max() - flight_data_df['daily_flights'].min()) *
                    (max_opacity - min_opacity)) + min_opacity

# Plot all the different connections
flight_paths = []
for i in range(len(flight_data_df)):
    fig.add_trace(
        go.Scattergeo(
            lon=[flight_data_df['lon_departure'][i], flight_data_df['lon_destination'][i]],
            lat=[flight_data_df['lat_departure'][i], flight_data_df['lat_destination'][i]],
            mode='lines',
            line=dict(width=1, color='white'),
            opacity=scaled_opacities[i],  # Use scaled opacities
            hoverinfo='skip',
        )
    )


# Update layout of the figure
fig.update_layout(
    title='Air Traffic Worldmap',
    showlegend=False,
)

# Update layout of the geospatial plot
fig.update_geos(
    projection_type="natural earth",
    resolution=50,
    showcoastlines=True, coastlinecolor="lightgrey",
    showland=True, landcolor="black",
    showocean=True, oceancolor="dimgrey",
    showlakes=True, lakecolor="black",
    showcountries=True, countrycolor="lightgrey",
    # lataxis_showgrid=True, lonaxis_showgrid=True
)

# Show the combined plot
fig.show()
