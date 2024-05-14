#######################################
# IMPORTS #############################
#######################################

import plotly.graph_objects as go
import data_transformation_pandas
from pathlib import Path

# Get the directory of the current file
current_directory = Path(__file__).resolve().parent


#######################################
# Data import #########################
#######################################

# Define the list of months
# month_list = ["01-January", "02-February", "03-March", "04-April", "05-May", "06-June", "07-July", "08-August", "09-September", "10-October", "11-November", "12-December"]
month_list = ["01-January", "02-February", "03-March", "04-April", "05-May", "06-June", "07-July", "08-August", "09-September", "10-October", "11-November", "12-December"]


# Dictionary to store connections by month
monthly_connections = {}

# Iterate over month_list to gather data and month names
for month in month_list:
    all_connections, sum_connections = data_transformation_pandas.process_flight_connections(month)

    # Store the DataFrames in a dictionary with the month as the key
    monthly_connections[month] = {
        "all_connections": all_connections,
        "sum_connections": sum_connections
    }


#######################################
# Plotting ############################
#######################################

# Function to generate monthly figure with buttons
def generate_monthly_figure():
    fig = go.Figure()

    # Define maximum and minimum sizes for the markers
    max_size = 20
    min_size = 2

    # Define maximum and minimum opacities for the flight paths
    max_opacity = 1
    min_opacity = 0.0

    counter = [0]
    total = 0

    # Get the global minimum and maximum values of daily flights across all months
    global_min_daily_flights = min([monthly_connections[month]["sum_connections"]["number_of_total_flights"].min() for month in month_list])
    global_max_daily_flights = max([monthly_connections[month]["sum_connections"]["number_of_total_flights"].max() for month in month_list])

    max_opacity = 1
    min_opacity = 0.0
    global_min_opacity = min([monthly_connections[month]["all_connections"]['averageDailyFlights'].min() for month in month_list])
    global_max_opacity = max([monthly_connections[month]["all_connections"]['averageDailyFlights'].max() for month in month_list])

    # Create traces for each month
    for month_data in month_list:

        # scale the values between min and max sizes
        scaled_sizes = ((monthly_connections[month_data]["sum_connections"]['number_of_total_flights'] - global_min_daily_flights) /
                        (global_max_daily_flights - global_min_daily_flights) *
                        (max_size - min_size)) + min_size

        # Plot the different airports for the month (markers)
        fig.add_trace(go.Scattergeo(
            lat=monthly_connections[month_data]["sum_connections"]["lat_departure"],
            lon=monthly_connections[month_data]["sum_connections"]["lon_departure"],
            text=monthly_connections[month_data]["sum_connections"]["departure_airport_name"] + '<br>' +
            "Number of average departing daily flights: " +
            monthly_connections[month_data]["sum_connections"]["number_of_total_flights"].apply(lambda x: round(x, 2)).astype(str),  # Round to 2 decimal places
            hoverinfo='text',  # Set hoverinfo to 'text'
            mode='markers',
            marker=dict(
                size=scaled_sizes,  # Scale the sizes between min and max sizes
                opacity=0.9,
                line_width=0,
                autocolorscale=False,
                colorscale='Bluered',
                cmin=global_min_daily_flights,  # Use global minimum value
                cmax=global_max_daily_flights,  # Use global maximum value,
                color=monthly_connections[month_data]["sum_connections"]['number_of_total_flights'],
                colorbar_title="Average Daily<br>Departing Flights"
            ),
            name=month_data,  # Set the name for the legend
            visible=False
        ))
        total += 1

        # Scale the opacities between min and max opacities for the flight paths
        scaled_opacities = ((monthly_connections[month_data]["all_connections"]['averageDailyFlights'] - global_min_opacity) /
                            (global_max_opacity - global_min_opacity) * (max_opacity - min_opacity)) + min_opacity

        # Plot all the different connections for the month (lines)
        for i in range(len(monthly_connections[month_data]["all_connections"])):
            fig.add_trace(
                go.Scattergeo(
                    lon=[monthly_connections[month_data]["all_connections"]['lon_departure'][i], monthly_connections[month_data]["all_connections"]['lon_destination'][i]],
                    lat=[monthly_connections[month_data]["all_connections"]['lat_departure'][i], monthly_connections[month_data]["all_connections"]['lat_destination'][i]],
                    mode='lines',
                    line=dict(width=1, color='white'),
                    opacity=scaled_opacities[i],  # Use scaled opacities
                    hoverinfo='skip',
                    showlegend=False,  # Do not include lines in legend
                    visible=False
                )
            )
            total += 1
        counter.append(total)

    # Create buttons for each month
    buttons = []
    i = 0
    for month_data in month_list:
        visibility = []
        for test in range(total):
            if test >= counter[i] and test < counter[i+1]:
                visibility.append(True)
            else:
                visibility.append(False)
        button = dict(
            label=month_data,
            method="update",
            args=[{"visible": visibility},
                  {"title": f"Departing flights: {month_data}",  # Added missing f string
                   "annotations": []}]
        )
        buttons.append(button)
        i += 1

    # Add buttons to the layout
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=buttons,
                showactive=True,
                x=0,
                xanchor='left',
                y=0,
                yanchor='top',
            )
        ],
        title='Air Traffic Worldmap',  # Set initial title
        showlegend=True,
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

    return fig

# Generate figure with buttons for navigation between months
generate_monthly_figure()
