# IMPORTS #############################
#######################################

import pandas as pd
import eurostat
import geopandas as gpd
from shapely.geometry import LineString
import country_converter as coco
import matplotlib.pyplot as plt
import os
import matplotlib.cm as mcm
import matplotlib.colors as mcolors
cm = 1/2.54  # for inches-cm conversion

#######################################
# Data ################################
#######################################


# Function to get flight data for a specific country
def get_flight_data(country_code, filter_pars):
    return eurostat.get_data_df(f'avia_par_{country_code}', filter_pars=filter_pars)


# Define country codes according to eurostat
country_codes = ['de', 'fr', 'uk', 'be', 'bg', 'dk', 'ee', 'ie', 'el', 'es', 'hr', 'it', 'cy', 'lv', 'lt', 'lu', 'hu', 'mt', 'nl', 'at', 'pl', 'pt', 'ro', 'si', 'sk', 'is', 'no', 'ch', 'me', 'mk', 'tr', 'rs']

# get flight data from different countries using eurostat bib
my_filter_pars = {'startPeriod': 2019, 'endPeriod': 2019, 'unit': 'FLIGHT', 'tra_meas': 'CAF_PAS', 'freq': 'A'}
country_data = {code: get_flight_data(code, my_filter_pars) for code in country_codes}

# get data for countrys + graticules
data_dir = "/Users/barend/Desktop/Thesis/demandmap/figures/worldmap/data/"
path_countries = "/Users/barend/Desktop/Thesis/demandmap/figures/data_general/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
countries = gpd.read_file(path_countries)
path_graticules = data_dir + "ne_50m_graticules_10/ne_50m_graticules_10.shp"
graticules = gpd.read_file(path_graticules)

# Edit Data ################################
############################################


# https://github.com/ip2location/ip2location-iata-icao?tab=readme-ov-file
# Read the CSV file conntaining the different airports into a Pandas DataFrame
airports_df = pd.read_csv(
    filepath_or_buffer='/Users/barend/Desktop/Thesis/demandmap/figures/worldmap/data/iata-icao.csv',
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


def generate_takeoff_details(data, airports_geodf):
    # Lists to store the details of takeoff airports
    icao_list = []
    total_flights_list = []
    geometry_list = []

    # Variables to track the current takeoff airport and total flights
    current_takeoff = None
    total_flights = 0

    # Iteration for each airport
    for airport_connections, flight in zip(data['airp_pr\TIME_PERIOD'], data['2019']):
        takeoff = airport_connections[3:7]

        # Check if takeoff is present in the 'icao' column of the GeoDataFrame
        if takeoff in airports_geodf['icao'].values:
            if takeoff != current_takeoff:
                # If the takeoff airport changes, update the total flights and reset the count
                if current_takeoff is not None:
                    icao_list.append(current_takeoff)
                    total_flights_list.append(total_flights)
                    geometry_list.append(airports_geodf.loc[airports_geodf['icao'] == current_takeoff, 'geometry'].iloc[0])

                current_takeoff = takeoff
                total_flights = 0

            # Increment total flights for the current takeoff airport
            total_flights += flight

    # Add the details for the last takeoff airport
    if current_takeoff is not None:
        icao_list.append(current_takeoff)
        total_flights_list.append(total_flights)
        geometry_list.append(airports_geodf.loc[airports_geodf['icao'] == current_takeoff, 'geometry'].iloc[0])

    # Create a DataFrame from the lists
    takeoff_df = gpd.GeoDataFrame(
        {'ICAO': icao_list, 'Total_Flights': total_flights_list},
        geometry=geometry_list,
        crs=airports_geodf.crs
    )

    return takeoff_df


# Generate takeoff details for all countries
takeoff_df = {code: generate_takeoff_details(data, airports_geodf) for code, data in country_data.items()}

# set coordinate reference system (crs) depening on map
# https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.set_crs.html
target_projection = "EPSG:3035"
# 3035 seems to work well for Europe

# change Data to adjusted crs
# https://automating-gis-processes.github.io/CSC/notebooks/L2/projections.html
countries = countries.to_crs(target_projection)
graticules = graticules.to_crs(target_projection)
country_gdfs = {code: gdf.to_crs(target_projection) for code, gdf in country_gdfs.items()}
takeoff_df = {code: gdf.to_crs(target_projection) for code, gdf in takeoff_df.items()}

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
    color='black',
    linewidth=0.5,
    linestyle='--',
    alpha=0.5,
)

ax.set_facecolor('grey')

# Countries colour ####################
# https://github.com/IndEcol/country_converter?tab=readme-ov-file#classification-schemes

cc = coco.CountryConverter()

for country in countries.itertuples():
    if country.CONTINENT == 'Europe':
        country_geo = gpd.GeoSeries(country.geometry)
        country_geo.plot(
            ax=ax,
            facecolor='black',
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


# def plotting circles for every airport corresponding the number of flights
def plot_airports(ax, geodf):
    max_flights = max(gdf['Total_Flights'].max() for gdf in geodf.values())
    cmap = plt.colormaps['cool']  # Choose a colormap
    norm = mcolors.Normalize(vmin=0, vmax=max_flights) # Define a normalization function
    for gdf in geodf.values():
        normalized_markersize = gdf['Total_Flights'] / max_flights * 500
        normalized_flights = gdf['Total_Flights']
        colors = cmap(norm(normalized_flights))
        gdf.plot(
            ax=ax,
            marker='o',  # Use circle marker
            color=colors,
            markersize=normalized_markersize,
            alpha=0.7  # Fixed alpha value
        )
    sm = mcm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.5)
    cbar.set_label('Total Flights')


# def for plotting the connections between different airports
def plot_connections(ax, geodfs, color='white'):
    max_flights = max(gdf['flights'].max() for gdf in geodfs.values())
    for gdf in geodfs.values():
        normalized_markersize = gdf['flights'] / max_flights * 0.2
        normalized_alpha = gdf['flights'] / max_flights * 0.5
        gdf.plot(
            ax=ax,
            marker='-',
            color=color,
            markersize=normalized_markersize,
            alpha=normalized_alpha
        )


# Plot airports with scaled marker size based on total flights
plot_airports(ax, takeoff_df)

# Plot airport connections for each country
plot_connections(ax, country_gdfs)


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
