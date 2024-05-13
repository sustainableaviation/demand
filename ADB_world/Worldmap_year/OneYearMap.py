#######################################
# IMPORTS #############################
#######################################

import plotly.graph_objects as go
import pandas as pd
import json
import os
import sys

# Get the directory of the current file
current_directory = os.path.dirname(__file__)
# Navigate one level up to get the parent directory
parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
# Add the parent directory to the Python path
sys.path.append(parent_directory)
import def_flight_connection  # Import custom flight connection module

# File path for storing flight connection data
file_path = os.path.join(parent_directory, "Airport Data/flight_connections_year.json")

#######################################
# Data import #########################
#######################################

# If the "flight_connections_year" file doesn't exist, generate and save flight connection data
if not os.path.exists(file_path):
    all_connections = []  # List to store all flight connections

    # Define the list of months
    month_list = ["01-January", "02-February", "03-March", "04-April", "05-May", "06-June",
                  "07-July", "08-August", "09-September", "10-October", "11-November", "12-December"]

    # Generate flight connection data for each month and save it
    for month in month_list:
        def_flight_connection.generate_flight_connections_json(month)

    # Process flight connections for January to create initial DataFrame
    connections_df, _ = def_flight_connection.process_flight_connections("01-January")

    # Iterate over month_list to gather and concatenate data
    for month in month_list[1:]:
        connections_data, _ = def_flight_connection.process_flight_connections(month)
        connections_df = pd.concat([connections_df, connections_data], ignore_index=True)

    # Consolidate connections with the same departure and destination
    connections_df = connections_df.groupby(["icao_departure", "icao_destination"], as_index=False).agg({
        "departure_airport_name": "first",
        "lat_departure": "first",
        "lon_departure": "first",
        "lat_destination": "first",
        "lon_destination": "first",
        "averageDailyFlights": lambda x: x.sum() / 12  # Divide the sum by 12 for annual average
    })

    # Convert DataFrame to dictionary and save as JSON file
    all_connections.append(connections_df.to_dict(orient='records'))
    with open(file_path, 'w') as f:
        json.dump(all_connections, f, indent=4)
    print(f"All connections saved to {file_path}")
else:
    print(f"The file '{file_path}' already exists.")

#######################################
# Plotting ############################
#######################################

# Process flight connection data for the entire year
flight_data_df, daily_flights_df = def_flight_connection.process_flight_connections("Year")

# Calculate the maximum value of 'daily_flights' column
max_daily_flights = daily_flights_df['number_of_total_flights'].max()

# number of total connections
total_connections = len(flight_data_df)

# Define maximum and minimum sizes for markers
max_size = 20
min_size = 2

# scale the values between min and max sizes
scaled_sizes = ((daily_flights_df['number_of_total_flights'] - daily_flights_df['number_of_total_flights'].min()) /
                (daily_flights_df['number_of_total_flights'].max() - daily_flights_df['number_of_total_flights'].min()) *
                (max_size - min_size)) + min_size

# Plot the different airport markers
fig = go.Figure(go.Scattergeo(
    lat=daily_flights_df["lat_departure"],
    lon=daily_flights_df["lon_departure"],
    text=daily_flights_df["departure_airport_name"] + '<br>'
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
        colorbar_title="Average Daily<br>Departing Flights<br>per year"
    )
))

# Define maximum and minimum opacities for flight connections
max_opacity = 1
min_opacity = 0.0

# Scale the opacities between min and max opacities
scaled_opacities = ((flight_data_df['averageDailyFlights'] - flight_data_df['averageDailyFlights'].min()) /
                    (flight_data_df['averageDailyFlights'].max() - flight_data_df['averageDailyFlights'].min()) *
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
    title=f'Air Traffic Worldmap<br>Number of total different connections: {total_connections}',
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

#######################################
# Export PDF ##########################
#######################################

# Define the file path for saving the PDF
pdf_file_path = os.path.join(current_directory, "Air_Traffic_Worldmap_year.pdf")

# Save the figure as a PDF in the same folder
fig.write_image(pdf_file_path, format="pdf")

# Print the path where the PDF is saved
print(f"Figure saved as PDF: {pdf_file_path}")
