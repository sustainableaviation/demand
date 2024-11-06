import plotly.graph_objects as go
import airport_check  # Assuming airport_check is a module or script containing airport_location function

#######################################
# Create world map ####################
#######################################

# Create the blank world map
fig = go.Figure()

def initialize_map():
    # Initialize the world map with the base configuration
    fig.add_trace(go.Choropleth(
        locations=[],  # No data for countries
        z=[],  # No data for color scale
    ))

    fig.update_layout(
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

initialize_map()

#######################################
# Functions ###########################
#######################################

# Initialize lists for departure, destination markers, and lines
departure_markers = []
destination_markers = []
flight_lines = []

# Function to retrieve airport location and add/update marker on map
def add_airport_marker_departure(location):
    """
    Add or update the departure airport marker on the map.

    Args:
        location (str): The ICAO code of the departure airport.
    """
    lat, lon = airport_check.airport_location(location)
    if lat is not None and lon is not None:
        # Add new departure marker
        departure_marker = go.Scattergeo(
            lon=[lon],
            lat=[lat],
            mode='markers',
            marker=dict(
                size=15,
                color='green',
                opacity=1,
            ),
            name=f"Departure: {location}",  # Add ICAO code to legend
            legendgroup='departure',
            legendrank=1,
            showlegend=False,  # Ensure legend is shown
            hoverinfo='text',  # Display text when hovering
            text=f"Departure: {location}"  # Custom text to display
        )
        fig.add_trace(departure_marker)
        departure_markers.append(departure_marker)
        
        # Check if a corresponding destination marker exists and add a flight line
        if len(departure_markers) == len(destination_markers):
            add_flight_line()

# Function to retrieve airport location and add/update marker on map
def add_airport_marker_destination(location):
    """
    Add or update the destination airport marker on the map.

    Args:
        location (str): The ICAO code of the destination airport.
    """
    lat, lon = airport_check.airport_location(location)
    if lat is not None and lon is not None:
        # Add new destination marker
        destination_marker = go.Scattergeo(
            lon=[lon],
            lat=[lat],
            mode='markers',
            marker=dict(
                size=15,
                color='orange',
                opacity=0.9,
            ),
            name=f"Destination: {location}",  # Add ICAO code to legend
            legendgroup='destination',
            legendrank=2,
            showlegend=False,  # Ensure legend is shown
            hoverinfo='text',  # Display text when hovering
            text=f"Destination: {location}"  # Custom text to display
        )
        fig.add_trace(destination_marker)
        destination_markers.append(destination_marker)
        
        # Check if a corresponding departure marker exists and add a flight line
        if len(departure_markers) == len(destination_markers):
            add_flight_line()

# Function to add/update flight line between departure and destination
def add_flight_line():
    """
    Add or update the flight line between the departure and destination airports on the map.
    """
    if len(departure_markers) > 0 and len(destination_markers) > 0:
        departure_marker = departure_markers[-1]
        destination_marker = destination_markers[-1]

        departure_lat = departure_marker['lat'][0]
        departure_lon = departure_marker['lon'][0]
        destination_lat = destination_marker['lat'][0]
        destination_lon = destination_marker['lon'][0]

        # Add new flight line
        flight_line = go.Scattergeo(
            lon=[departure_lon, destination_lon],
            lat=[departure_lat, destination_lat],
            mode='lines',
            line=dict(width=5, color='White'),
            showlegend=False,  # Do not show flight path in the legend
            hoverinfo=None
        )
        fig.add_trace(flight_line)
        flight_lines.append(flight_line)

# Function to clear existing points on the map
def reset_map():
    global departure_markers, destination_markers, flight_lines
    # Clear all markers and lines
    fig.data = []
    # Reset lists of markers and lines
    departure_markers = []
    destination_markers = []
    flight_lines = []
    # Reinitialize the base map
    initialize_map()

