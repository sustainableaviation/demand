import pandas as pd
import sys
from pathlib import Path
import data_preperation
import plotly.express as px
import plotly.graph_objects as go  # Zum Zugriff auf Plotly Graph Objects



# Determine the current directory
current_directory = Path(__file__).resolve().parent

# Add the path to the api_aerodatabox folder to sys.path
api_aerodatabox_path = current_directory.parents[0] / 'api_aerodatabox'

airport_df = data_preperation.prepare_airport_data()

# Ensure the correct module path is added
current_directory = Path(__file__).resolve().parent
api_aerodatabox_path = current_directory.parents[0] / 'api_aerodatabox'
sys.path.insert(0, str(api_aerodatabox_path))

import data_transformation_pandas

# Process flight connections to get DataFrame
flight_data_df, daily_flights_df = data_transformation_pandas.process_flight_connections("Year")

# Merge daily_flights_df with airport_df to add country code
daily_flights_df = daily_flights_df.merge(airport_df[['airport_name', 'country_code']],
                                          left_on='departure_airport_name', right_on='airport_name', how='left')


# Read the CSV file into a DataFrame (assuming 'country-coord.csv' contains country coordinates)
df = pd.read_csv('country-coord.csv')

# Group by departure_country and sum the number of departing flights
grouped_df = daily_flights_df.groupby('country_code')['number_of_total_flights'].sum().reset_index()

# Rename columns for clarity and consistency
grouped_df.columns = ["Alpha-2 code", "Total Departing Flights"]

# Merge with the coordinates DataFrame (df) on 'Alpha-2 code'
grouped_df = pd.merge(grouped_df, df, on='Alpha-2 code', how='left')

# Print the resulting DataFrame
print(grouped_df)

# Filtern Sie NaN-Werte aus, da Plotly damit möglicherweise Probleme hat
df = grouped_df.dropna(subset=['Latitude (average)', 'Longitude (average)'])

# Funktion zur Erstellung der Weltkarte und Hinzufügen der Punkte
def create_country_map():
    # Erstellen der leeren Figur
    fig = go.Figure()

    # Update the layout for the map
    fig.update_layout(
        geo=dict(
            showframe=True,
            projection_type="natural earth",
            showcoastlines=True, coastlinecolor="lightgrey",
            showland=True, landcolor="black",
            showocean=True, oceancolor="dimgrey",
            showlakes=True, lakecolor="black",
            showcountries=True, countrycolor="lightgrey",
        ),
        margin=dict(l=10, r=10, t=10, b=10),
    )

    # Plotly Express verwenden, um die Punkte hinzuzufügen
    scatter = px.scatter_geo(df,
                             lat="Latitude (average)",
                             lon="Longitude (average)",
                             size="Total Departing Flights",  # Größe der Punkte basierend auf abgehenden Flügen
                             hover_name="Country",  # Ländername beim Überfahren anzeigen
                             hover_data=["Total Departing Flights"],  # Zusätzliche Daten zum Anzeigen beim Überfahren
                             projection="natural earth",  # Projektion der Karte
                             title="Weltkarte mit Punkten für abgehende Flüge")

    # Hinzufügen der Punkte zur bestehenden Weltkarte
    fig.add_trace(scatter.data[0])  # Fügt den Scatterplot zur bestehenden Figur hinzu

    return fig
