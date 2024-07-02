#######################################
# IMPORTS #############################
#######################################


import plotly.graph_objects as go
import sys
from pathlib import Path

# Ensure the correct module path is added
current_directory = Path(__file__).resolve().parent
api_aerodatabox_path = current_directory.parents[0] / 'api_aerodatabox'
sys.path.insert(0, str(api_aerodatabox_path))

import data_transformation_pandas


def create_flight_connections_plot(fig, plot_whole_year, month=None):
    """
        Create a plot of flight connections on a geographic map.

        Args:
            fig (go.Figure): The Plotly figure object to add traces to.
            plot_whole_year (bool): Whether to plot data for the whole year.
            month (str, optional): Specific month to plot data for. Defaults to None.

        Returns:
            go.Figure: The updated Plotly figure object with all flight connections plotted.

    """
    # Plotting
    flight_data_df, daily_flights_df = data_transformation_pandas.process_flight_connections("Year")

    # Calculate the maximum value of 'daily_flights' column
    max_daily_flights = daily_flights_df['number_of_total_flights'].max()

    flight_data_df = flight_data_df[flight_data_df['averageDailyFlights'] > 1].reset_index(drop=True)

    # Define maximum and minimum sizes for markers
    max_size = 20
    min_size = 2

    # Scale the values between min and max sizes
    scaled_sizes = ((daily_flights_df['number_of_total_flights'] - daily_flights_df['number_of_total_flights'].min()) /
                    (daily_flights_df['number_of_total_flights'].max() - daily_flights_df['number_of_total_flights'].min()) *
                    (max_size - min_size)) + min_size

    # Plot the different airport markers
    fig.add_trace(go.Scattergeo(
        lat=daily_flights_df["lat_departure"],
        lon=daily_flights_df["lon_departure"],
        text=daily_flights_df["departure_airport_name"] + '<br>'
        + "Number of average departing daily flights: "
        + daily_flights_df["number_of_total_flights"].apply(lambda x: round(x, 2)).astype(str),  # Round to 2 decimal places
        hoverinfo='text',  # Set hoverinfo to 'text'
        mode='markers',
        showlegend=False,
        marker=dict(
            size=scaled_sizes,  # Scale the sizes between min and max sizes
            opacity=0.9,
            line_width=0,
            autocolorscale=False,
            colorscale='Bluered',
            cmin=0,
            color=daily_flights_df['number_of_total_flights'],
            cmax=max_daily_flights,
            colorbar=dict(
                title=dict(
                    text="Average flights per day",
                    side="top"
                ),
                orientation='h',  # Horizontal orientation
                y=-0.0,  # Position below the map
                x=0.5,
                xanchor='center',
                yanchor='top'
            )
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
    for i in range(len(flight_data_df)):
        fig.add_trace(
            go.Scattergeo(
                lon=[flight_data_df['lon_departure'][i], flight_data_df['lon_destination'][i]],
                lat=[flight_data_df['lat_departure'][i], flight_data_df['lat_destination'][i]],
                mode='lines',
                line=dict(width=1, color='white'),
                opacity=scaled_opacities[i],  # Use scaled opacities
                hoverinfo='skip',
                showlegend=False,
            )
        )

    return fig
