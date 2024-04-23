# IMPORTS #############################
#######################################

import json
import pandas as pd
import geopandas as gpd
import os
import country_converter as coco
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import matplotlib.colors as mcolors
import matplotlib.cm as mcm

cm = 1/2.54  # for inches-cm conversion

#######################################
# Data ################################
#######################################

# get data for countrys + graticules
data_dir = "/Users/barend/Desktop/Thesis/demandmap/figures/worldmap/data/"
path_countries = "/Users/barend/Desktop/Thesis/demandmap/figures/data_general/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
countries = gpd.read_file(path_countries)
path_graticules = data_dir + "ne_50m_graticules_10/ne_50m_graticules_10.shp"
graticules = gpd.read_file(path_graticules)

# Read JSON file
with open('/Users/barend/Desktop/Thesis/demandmap/ADB/Airport Data/LSZH.json', 'r') as f:
    data = json.load(f)

# Extract desired fields
connections = []  # creates empty list
for route in data['routes']:
    icao = route['destination'].get('icao')  # takes icao as an element -> returns None if no icao indicated
    if icao is not None:
        route_info = {
            'icao': icao,
            'lat': route['destination']['location']['lat'],
            'lon': route['destination']['location']['lon'],
            'averageDailyFlights': route['averageDailyFlights']
        }
        connections.append(route_info)  # appends it to list

# Create DataFrame
connections_df = pd.DataFrame(connections)


airports_geodf = gpd.GeoDataFrame(
        connections_df,
        geometry=gpd.points_from_xy(
            x=connections_df["lon"],
            y=connections_df["lat"],
            # Specify the coordinate reference system (standard for lat/lon)
            crs='EPSG:4326'
        )
    )


# Zurich #

# Create GeoDataFrame for Zurich
zurich_geodf = gpd.GeoDataFrame(
    {
        'icao': ["LSZH"],
        'lat': [47.464722],
        'lon': [8.549167],
    },
    geometry=gpd.points_from_xy(
        x=[8.549167],
        y=[47.464722],
    ),
    crs='EPSG:4326'
)


# Edit Data ################################
############################################

# Connections #
connection_geometries = []

for index, landing in airports_geodf.iterrows():
    landing_geometry = landing['geometry']
    takeoff_geometry = zurich_geodf.at[0, 'geometry']
    line_geometry = LineString([takeoff_geometry, landing_geometry])
    connection_geometries.append(line_geometry)

connections_geodf = gpd.GeoDataFrame(
    connections_df,
    geometry=connection_geometries,
    crs='EPSG:4326'
    )

# set coordinate reference system (crs) depening on map
# https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.set_crs.html
target_projection = "EPSG:4326"
# 3035 seems to work well for Europe

# change Data to adjusted crs
# https://automating-gis-processes.github.io/CSC/notebooks/L2/projections.html
countries = countries.to_crs(target_projection)
graticules = graticules.to_crs(target_projection)
airports_geodf = airports_geodf.to_crs(target_projection)
zurich_geodf = zurich_geodf.to_crs(target_projection)
connections_geodf = connections_geodf.to_crs(target_projection)


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
zurich_geodf.plot(
            ax=ax,
            marker='o',
            color='blue',
            markersize=10,
            alpha=0.5,
)

# plot Zurich airport location
max_flights = connections_geodf['averageDailyFlights'].max()
cmap = plt.colormaps['cool']  # Choose a colormap
norm = mcolors.Normalize(vmin=0, vmax=max_flights)  # Define a normalization function
normalized_flights = airports_geodf['averageDailyFlights']
airports_geodf.plot(
            ax=ax,
            color=cmap(norm(normalized_flights)),
            markersize=connections_geodf['averageDailyFlights'] / max_flights*15,
            alpha=0.5,
            linewidth=0.1,
)

# plot all destination airports
connections_geodf.plot(
            ax=ax,
            marker='-',
            color='white',
            alpha=connections_geodf['averageDailyFlights'] / max_flights,
            linewidth=0.25,
)

# plot all connections
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
