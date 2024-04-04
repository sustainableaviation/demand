# IMPORTS #############################
#######################################

import pandas as pd
import eurostat
import geopandas as gpd
from shapely.geometry import LineString
import country_converter as coco
import matplotlib.pyplot as plt
import os
cm = 1/2.54  # for inches-cm conversion

# Data ################################
#######################################

# Function to get flight data for a specific country


def get_flight_data(country_code, filter_pars):
    return eurostat.get_data_df(f'avia_par_{country_code}', filter_pars=filter_pars)


# Define country codes
country_codes = ['de', 'fr', 'uk', 'be', 'bg', 'dk', 'ee', 'ie', 'el', 'es', 'hr', 'it', 'cy', 'lv', 'lt', 'lu', 'hu', 'mt', 'nl', 'at', 'pl', 'pt', 'ro', 'si', 'sk', 'is', 'no', 'ch', 'me', 'mk', 'tr', 'rs']

# get flight data from different countries using eurostat bib
my_filter_pars = {'startPeriod': 2019, 'endPeriod': 2019, 'unit': 'FLIGHT', 'tra_meas': 'CAF_PAS', 'freq': 'A'}
# Get flight data for all countries
country_data = {code: get_flight_data(code, my_filter_pars) for code in country_codes}


# get data for countrys
data_dir = "/Users/barend/Desktop/Thesis/demandmap/figures/worldmap/"
path_countries = data_dir + "ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
countries = gpd.read_file(path_countries)
path_graticules = data_dir + "ne_50m_graticules_10/ne_50m_graticules_10.shp"
graticules = gpd.read_file(path_graticules)

# Edit Data ################################
############################################


# https://github.com/ip2location/ip2location-iata-icao?tab=readme-ov-file
# Read the CSV file conntaining the different airports into a Pandas DataFrame
airports_df = pd.read_csv(
    filepath_or_buffer='/Users/barend/Desktop/Thesis/demandmap/figures/worldmap/iata-icao.csv',
    sep=',',  # seperation indicator
    header='infer',
    index_col=False,
)

# create a GeoDataFrame with the locations of the airports
airports_geodf = gpd.GeoDataFrame(
        airports_df,
        geometry=gpd.points_from_xy(
            x=airports_df["longitude"],
            y=airports_df["latitude"],
            # Specify the coordinate reference system (standard for lat/lon)
            crs='EPSG:4326'
        )
    )


# Create a GeoDataFrame with names, number of flights, and geometric connection
def create_geo_dataframe(data, airports_geodf):
    # Empty lists to store the line geometries and the corresponding data
    geometries = []
    names = []
    flights = []

    # Iteration for each connection
    for airport_connections, name, flight in zip(data['airp_pr\TIME_PERIOD'], data['airp_pr\TIME_PERIOD'], data['2019']):
        takeoff = airport_connections[3:7]
        landing = airport_connections[11:]

        # Check if takeoff and landing are present in the 'icao' column of the GeoDataFrame
        if takeoff in airports_geodf['icao'].values and landing in airports_geodf['icao'].values:
            # Index of the departure airport
            takeoff_index = airports_geodf[airports_geodf['icao'] == takeoff].index[0]
            # Index of the destination airport
            landing_index = airports_geodf[airports_geodf['icao'] == landing].index[0]
            # Create line between the departure and destination airports
            takeoff_geometry = airports_geodf.at[takeoff_index, 'geometry']
            landing_geometry = airports_geodf.at[landing_index, 'geometry']
            line_geometry = LineString([takeoff_geometry, landing_geometry])

            # Add the line geometry and corresponding data to the lists
            geometries.append(line_geometry)
            names.append(name)
            flights.append(flight)

    gdf = gpd.GeoDataFrame({'name': names, 'flights': flights, 'geometry': geometries}, crs='EPSG:4326')
    return gdf


# Create GeoDataFrame for each country
country_gdfs = {code: create_geo_dataframe(data, airports_geodf) for code, data in country_data.items()}


# set coordinate reference system (crs) depening on map
# https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.set_crs.html
target_projection = "EPSG:3035"
# 3035 seems to work well for Europe

# change Data to adjusted crs
# https://automating-gis-processes.github.io/CSC/notebooks/L2/projections.html
countries = countries.to_crs(target_projection)
graticules = graticules.to_crs(target_projection)
country_gdfs = {code: gdf.to_crs('EPSG:3035') for code, gdf in country_gdfs.items()}

# represent the lower-left and upper-right corners of a bounding box on a map (showing only part of whole map)
# https://geopandas.org/en/stable/docs/reference/api/geopandas.points_from_xy.html#geopandas-points-from-xy

lower_left = gpd.points_from_xy(
    x=[-10],  # longitude
    y=[33],  # latitude
    crs='EPSG:4326'  # = World Geodetic System WGS 84, defines an Earth-centered, Earth-fixed coordinate system
).to_crs(target_projection)

upper_right = gpd.points_from_xy(
    x=[60],  # longitude
    y=[60],  # latitude
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
    dpi=300,  # resolution of the figure
    figsize=(18*cm, 18*cm),  # A4=(210x297)mm,
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

graticules.plot(
    ax=ax,
    color='grey',
    linewidth=0.5,
    linestyle='--',
    alpha=0.5,
)


# Countries colour ####################

# https://github.com/IndEcol/country_converter?tab=readme-ov-file#classification-schemes

cc = coco.CountryConverter()

for country in countries.itertuples():
    if country.CONTINENT == 'Europe':
        # Convert the geometry to a GeoSeries
        country_geo = gpd.GeoSeries(country.geometry)
        # Plot the country with light blue color if it's in Europe
        country_geo.plot(
            ax=ax,
            facecolor='darkblue',
            edgecolor='black',
            linewidth=1)
    else:
        country_geo = gpd.GeoSeries(country.geometry)  # Convert the geometry to a GeoSeries
        country_geo.plot(
            ax=ax,
            facecolor='darkgreen',
            edgecolor='black',
            linewidth=1
        )


def plot_airports(ax, geodfs, color='red'):
    max_flights = max(gdf['flights'].max() for gdf in geodfs.values())
    for gdf in geodfs.values():
        normalized_markersize = gdf['flights'] / max_flights * 0.5  
        normalized_alpha = gdf['flights'] / max_flights * 0.5  
        gdf.plot(
            ax=ax,
            marker='-',
            color=color,
            markersize=normalized_markersize,
            alpha=normalized_alpha
        )


# Plot airport connections for each country
plot_airports(ax, country_gdfs)

######################################################
# EXPORT #############################################
######################################################


file_path = os.path.abspath(__file__)
file_name = os.path.splitext(os.path.basename(file_path))[0]
figure_name: str = str(file_name + '.pdf')

plt.savefig(
    fname=figure_name,
    format="pdf",
    bbox_inches='tight',
    transparent=False
)
