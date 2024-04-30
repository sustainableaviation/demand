# IMPORTS #############################
#######################################

import json
import pandas as pd
import geopandas as gpd
import os
import country_converter as coco
import matplotlib.pyplot as plt
from shapely.geometry import Point
import matplotlib.colors as mcolors
import matplotlib.cm as mcm
from shapely.wkt import loads

cm = 1/2.54  # for inches-cm conversion

#######################################
# Data ################################
#######################################

current_directory = os.path.dirname(os.path.realpath(__file__))  # Get the current directory

# get data for countrys + graticules
data_dir = "/Users/barend/Desktop/Thesis/demandmap/figures/worldmap/data/"
path_countries = "/Users/barend/Desktop/Thesis/demandmap/figures/data_general/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
countries = gpd.read_file(path_countries)
path_graticules = data_dir + "ne_50m_graticules_10/ne_50m_graticules_10.shp"
graticules = gpd.read_file(path_graticules)

# get connection data
file_path = os.path.join(current_directory, "Airport Data/airport_connections.json")
with open(file_path, 'r') as f:
    connection_data = json.load(f)

# Initialize lists to hold data
departures = []
landings = []
daily_flights = []
lines = []

# Iterate over each list of connections
for departing_airport in connection_data:
    for landing_airport in departing_airport:
        # Extract data from JSON
        departure = landing_airport['icao_departure']
        landing = landing_airport['icao_landing']
        daily_flight = landing_airport['averageDailyFlights']
        line_wkt = landing_airport['line_geometry']
        # Convert WKT to LineString
        line = loads(line_wkt)
        # Append data to lists
        lines.append(line)
        departures.append(departure)
        landings.append(landing)
        daily_flights.append(daily_flight)

# Create DataFrame
flight_data = {
    'departure': departures,
    'landing': landings,
    'daily_flights': daily_flights,
    'geometry': lines
}
flight_data_df = pd.DataFrame(flight_data)

# Create GeoDataFrame
flight_data_geodf = gpd.GeoDataFrame(flight_data_df, geometry='geometry')

print(flight_data_geodf)

# get the number of daily_flights per airport
# Initialize lists to hold aggregated data
departure_icao_list = []
number_of_total_flights_list = []
lat_lon_departure_list = []

# Iterate over the provided data
for connection_list in connection_data:
    # Initialize dictionaries to store flights and total daily flights for each departure airport
    flights_by_departure = {}
    total_flights_by_departure = {}

    # Iterate over each flight connection
    for connection in connection_list:
        departure_icao = connection["icao_departure"]
        daily_flights = connection["averageDailyFlights"]

        # Sum up daily flights for each departure airport
        if departure_icao in flights_by_departure:
            flights_by_departure[departure_icao] += daily_flights
        else:
            flights_by_departure[departure_icao] = daily_flights

    # Iterate over flights by departure airport to create a list of aggregated data
    for departure_icao, total_flights in flights_by_departure.items():
        departure_icao_list.append(departure_icao)
        number_of_total_flights_list.append(total_flights)
        # Find the corresponding departure coordinates
        for connection in connection_list:
            if connection["icao_departure"] == departure_icao:
                lat_lon_departure_list.append((connection["lat_departure"], connection["lon_departure"]))
                break

# Create DataFrame
flight_data = {
    'departure_icao': departure_icao_list,
    'number_of_total_flights': number_of_total_flights_list,
    'lat_lon_departure': lat_lon_departure_list
}
daily_flights_df = pd.DataFrame(flight_data)

# Create GeoDataFrame
geometry = [Point(lon, lat) for lat, lon in lat_lon_departure_list]
crs = {'init': 'epsg:4326'}  # Assuming WGS84 coordinate system
daily_flights_geodf = gpd.GeoDataFrame(daily_flights_df, geometry=geometry, crs=crs)

print(daily_flights_geodf)


# set coordinate reference system (crs) depening on map
# https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.set_crs.html
target_projection = "EPSG:4326"
# 3035 seems to work well for Europe

# change Data to adjusted crs
# https://automating-gis-processes.github.io/CSC/notebooks/L2/projections.html
countries = countries.to_crs(target_projection)
graticules = graticules.to_crs(target_projection)
flight_data_geodf.crs = target_projection
daily_flights_geodf = daily_flights_geodf.to_crs(target_projection)

# represent the lower-left and upper-right corners of a bounding box on a map (showing only part of whole map)
# https://geopandas.org/en/stable/docs/reference/api/geopandas.points_from_xy.html#geopandas-points-from-xy

lower_left = gpd.points_from_xy(
    x=[-180],  # longitude
    y=[-90],  # latitude
    crs='EPSG:4326'  # = World Geodetic System WGS 84, defines an Earth-centered, Earth-fixed coordinate system
).to_crs(target_projection)

upper_right = gpd.points_from_xy(
    x=[180],  # longitude
    y=[90],  # latitude
    crs='EPSG:4326'  # = WGS 84
).to_crs(target_projection)

######################################################
# Plot ###############################################
######################################################

# Set up Plot ###############

fig, ax = plt.subplots(
    num='main',
    nrows=1,  # only 1 plot
    ncols=1,  # only 1 plot
    dpi=500,  # resolution of the figure
    figsize=(50*cm, 50*cm),  # A4=(210x297)mm,
)

countries.plot(
    ax=ax,
    color='white',
    edgecolor='black',
    linewidth=0.25,
    alpha=1,  # transparency of the polygons
)

# AXIS LIMITS ################

ax.set_xlim(
    lower_left.x[0],
    upper_right.x[0]
)

ax.set_ylim(
    lower_left.y[0],
    upper_right.y[0]
)

# GRIDS ######################

ax.set_facecolor('grey')

# Countries colour ####################
# https://github.com/IndEcol/country_converter?tab=readme-ov-file#classification-schemes

cc = coco.CountryConverter()

for country in countries.itertuples():
    if country.CONTINENT == 'Europe':
        country_geo = gpd.GeoSeries(country.geometry)
        country_geo.plot(
            ax=ax,
            facecolor='darkgrey',
            edgecolor='silver',
            linewidth=0.5)
    else:
        country_geo = gpd.GeoSeries(country.geometry)
        country_geo.plot(
            ax=ax,
            facecolor='darkgrey',
            edgecolor='silver',
            linewidth=0.5
        )


max_flights = flight_data_geodf['daily_flights'].max()
flight_data_geodf.plot(
            ax=ax,
            marker='-',
            color='white',
            alpha=flight_data_geodf['daily_flights'] / max_flights,
            linewidth=0.5,
)

# plot Zurich airport location
max_daily_flights = daily_flights_geodf['number_of_total_flights'].max()
cmap = plt.colormaps['cool']  # Choose a colormap
norm = mcolors.Normalize(vmin=0, vmax=max_daily_flights)  # Define a normalization function
normalized_flights = daily_flights_geodf['number_of_total_flights']
daily_flights_geodf.plot(
            ax=ax,
            color=cmap(norm(normalized_flights)),
            markersize=daily_flights_geodf['number_of_total_flights'] / max_daily_flights*50,
            alpha=1,
            linewidth=0.1,
)

# plot legend
sm = mcm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, shrink=0.5)
cbar.set_label('Average Daily Flights')

######################################################
# EXPORT #############################################
######################################################

file_path = os.path.abspath(__file__)
folder_path = os.path.dirname(file_path)
file_name = os.path.splitext(os.path.basename(file_path))[0]
pdf_path = os.path.join(folder_path, file_name + '.pdf')

plt.savefig(
    fname=pdf_path,
    format="pdf",
    bbox_inches='tight',
    transparent=False
)
