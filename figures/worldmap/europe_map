# IMPORTS #######################################

# plotting
import matplotlib.pyplot as plt
import pandas as pd
import os
import country_converter as coco
# import matplotlib.font_manager as font_manager
# geographic plotting
import geopandas as gpd
# from shapely.geometry import LineString
# unit conversion
cm = 1/2.54  # for inches-cm conversion
# time manipulation
# from datetime import datetime
# data science
# import numpy as np

# Update Matplotlib parameters to customize text and font settings for plots
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Arial",
    "font.sans-serif": "Computer Modern",
    'font.size': 12
})

######################################################
# Import & adjust Data ###############################
######################################################

data_dir = "/Users/barend/Desktop/Thesis/demandmap/figures/worldmap/"
path_countries = data_dir + "ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
countries = gpd.read_file(path_countries)
path_graticules = data_dir + "ne_50m_graticules_10/ne_50m_graticules_10.shp"
graticules = gpd.read_file(path_graticules)


def import_airports_csv(filepath: str) -> gpd.GeoDataFrame:
    df = pd.read_csv(  # Read the CSV file into a pandas DataFrame
        filepath_or_buffer=filepath,
        sep=';',
        header='infer',
        index_col=False,
    )
    # Split the 'Position' column into separate 'lat' and 'lon' columns
    df[['lat', 'lon']] = df['Position'].str.split(',', expand=True)
    # Select only the relevant columns: 'Airport', 'lat', 'lon', 'Passenger'
    df = df[['Airport', 'lat', 'lon', 'Passenger']]
    # Create a GeoDataFrame from the DataFrame, adding a 'geometry' column with Point geometries
    geodf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            x=df['lon'],
            y=df['lat'],
            # Specify the coordinate reference system (standard for lat/lon)
            crs='EPSG:4326'
        )
    )
    return geodf


# change imported data into a GeoDataFrame
geodf_airports = import_airports_csv('/Users/barend/Desktop/Thesis/demandmap/figures/worldmap/airports.csv')


airport_connections = pd.read_csv(
    filepath_or_buffer='/Users/barend/Desktop/Thesis/demandmap/figures/worldmap/connections.csv',
    sep=';',
    header='infer',
)

######################################################
# GEOGRAPHY SETUP ####################################
######################################################


# set coordinate reference system (crs) depening on map
# https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.set_crs.html
target_projection = "EPSG:3035"
# 3035 seems to work well for Europe

# change Data to adjusted crs
# https://automating-gis-processes.github.io/CSC/notebooks/L2/projections.html
countries = countries.to_crs(target_projection)
graticules = graticules.to_crs(target_projection)
geodf_airports = geodf_airports.to_crs(target_projection)


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


# Airports ####################

geodf_airports.plot(
            ax=ax,
            marker='o',
            color='red',
            markersize=geodf_airports['Passenger']/150000,
            alpha=0.5,
)

# Connections ####################

for start in range(len(geodf_airports)-1):
    current_airport = geodf_airports.iloc[start]
    for end in range(len(geodf_airports)-1):
        next_airport = geodf_airports.iloc[end]
        if airport_connections.iloc[end, start] != 0:
            # Plot a line connecting the current airport with the next airport
            ax.plot(
                [current_airport.geometry.x, next_airport.geometry.x],
                [current_airport.geometry.y, next_airport.geometry.y],
                color='orange',
                linestyle='-',
                linewidth=airport_connections.iloc[start, end+1]/15000,
                alpha=airport_connections.iloc[start, end+1]/17000
            )
        else:
            # If the value is 0, do not plot a line
            pass


print(airport_connections)
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
