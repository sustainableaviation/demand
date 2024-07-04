import pandas as pd
import sys
from pathlib import Path
import data_preperation
import plotly.express as px
import plotly.graph_objects as go  # Zum Zugriff auf Plotly Graph Objects

# Determine the current directory
current_directory = Path(__file__).resolve().parent
api_aerodatabox_path = current_directory.parents[0] / 'api_aerodatabox'

airport_df = data_preperation.prepare_airport_data()

# Ensure the correct module path is added
current_directory = Path(__file__).resolve().parent
api_aerodatabox_path = current_directory.parents[0] / 'api_aerodatabox'
sys.path.insert(0, str(api_aerodatabox_path))

import data_transformation_pandas


# Process flight connections to get DataFrame
flight_data_df, daily_flights_df = data_transformation_pandas.process_flight_connections("Year")


# Create the blank world map
country_map = go.Figure(data=go.Choropleth(
    locations=[],  # No data for countries
    z=[],  # No data for color scale
))

# Update the layout for the map
country_map.update_layout(
    geo=dict(
        showframe=True,
        projection_type="natural earth",
        showcoastlines=True, coastlinecolor="lightgrey",
        showland=True, landcolor="black",
        showocean=True, oceancolor="dimgrey",
        showlakes=True, lakecolor="black",
        showcountries=True, countrycolor="lightgrey",
    ),

    margin=dict(l=10, r=10, t=10, b=70),
    legend=dict(
        y=0,  # Position the legend below the map
        x=0.5,
        xanchor='center',
        yanchor='top'
    ),
)

# Function to clear existing points on the map
def clear_map(fig):
    while fig.data:
        fig.data = []

#######################################
# Function to plot country mode
#######################################

# Merge daily_flights_df with airport_df to add country code
country_map_df = daily_flights_df.merge(airport_df[['airport_name', 'country_code']],
                                          left_on='departure_airport_name', right_on='airport_name', how='left')

# Read the CSV file into a DataFrame (assuming 'country-coord.csv' contains country coordinates)
country_coord_df = pd.read_csv('country-coord.csv')

# Group by departure_country and sum the number of departing flights
country_map_grouped_df = country_map_df.groupby('country_code')['number_of_total_flights'].sum().reset_index()

# Rename columns for clarity and consistency
country_map_grouped_df.columns = ["Alpha-2 code", "Total Departing Flights"]

# Merge with the coordinates DataFrame (df) on 'Alpha-2 code'
country_map_grouped_df = pd.merge(country_map_grouped_df, country_coord_df, on='Alpha-2 code', how='left')

# Filtern Sie NaN-Werte aus, da Plotly damit möglicherweise Probleme hat
country_map_filtered_df = country_map_grouped_df.dropna(subset=['Latitude (average)', 'Longitude (average)'])
country_map_filtered_df["Total Departing Flights"] = country_map_filtered_df["Total Departing Flights"].apply(lambda x: round(x, 2))

print(country_map_filtered_df)

# Function to create a choropleth map coloring countries based on departing flights
def create_country_map():
    # Clear existing points
    clear_map(country_map)

    # Use Plotly Express to create a choropleth map
    choropleth = px.choropleth(
        country_map_filtered_df,
        locations="Alpha-3 code",  # Column with country names
        locationmode="ISO-3",  # Mode to match country names
        color="Total Departing Flights",  # Column with data to color the countries
        hover_name="Country",  # Display country name when hovering
        hover_data={"Total Departing Flights": True},  # Additional data to display when hovering
        projection="natural earth",  # Map projection
        color_continuous_scale=px.colors.sequential.Plasma  # Color scale for the map
    )

    # Add the choropleth map to the existing world map
    country_map.add_trace(choropleth.data[0])  # Add the choropleth to the existing figure

def create_pie_chart_country():
    # Assuming country_map_filtered_df is your DataFrame containing the data
    pie_chart = px.pie(
        country_map_filtered_df,
        values="Total Departing Flights",
        names="Country",
        title="Total Departing Flights by Country",
        hover_data=["Total Departing Flights"],  # Hover data to display on mouseover
        labels={"Total Departing Flights": "Total Departing Flights"}  # Labels for hover data
    )
    
    pie_chart.update_traces(textposition='inside', textinfo='percent+label')
    pie_chart.update_layout(showlegend=False)  # Hide the legend
    
    return pie_chart



#######################################
# Function to plot continent mode
#######################################

# Group by departure_country and sum the number of departing flights
continent_map_df = daily_flights_df.groupby('departure_continent')['number_of_total_flights'].sum().reset_index()
continent_loc = {
        'departure_continent': ["Africa", "Asia", "Australia & Oceania", "Europe", "North America",  "South America"],
        'lat': [10.0000, 40.0000, -27.000, 48.0000, 38.0000, -10.0000],
        'lon': [20.0000, 95.0000, 133.0000, 9.0000, -97.0000,-55.0000],
    }
continent_loc_df = pd.DataFrame(continent_loc)
continent_df = pd.merge(continent_map_df, continent_loc_df, on='departure_continent', how='left')
continent_df.columns = ["Continent", "Total Departing Flights", "lat", "lon"]
# Round the "Total Departing Flights" column to 2 decimal places
continent_df["Total Departing Flights"] = continent_df["Total Departing Flights"].round(2)

print(continent_df)

# Define a consistent color scale for the continents
color_scale = px.colors.qualitative.Plotly
color_map = {continent: color for continent, color in zip(continent_df["Continent"], color_scale)}

def create_continent_map():
    # Clear existing points
    clear_map(country_map)
    # Use Plotly Express to add points
    scatter = px.scatter_geo(
        continent_df,
        lat="lat",
        lon="lon",
        size="Total Departing Flights",  # Size of points based on departing flights
        size_max=50,  # Max size of the points
        hover_name="Continent",  # Display country name when hovering
        hover_data={'Total Departing Flights': True, "lat": False, "lon": False},  # Additional data to display when hovering, with lat/lon hidden
        projection="natural earth",  # Map projection
        color="Total Departing Flights",
    )

    # Add the points to the existing world map
    country_map.add_trace(scatter.data[0])  # Add the scatter plot to the existing figure

# Create the Plotly pie chart
def create_pie_chart_continent():
    pie_chart = px.pie(
        continent_df,
        names="Continent",
        values="Total Departing Flights",
        color="Continent",
        color_discrete_map=color_map,  # Use the color map for consistent colors
        title="Total Departing Flights by Continent"
    )
    pie_chart.update_traces(textposition='inside', textinfo='percent+label')
    pie_chart.update_layout(showlegend=False)  # Hide the legend
    return pie_chart
