#%%
# runs code as interactive cell 
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

# plotting
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
# geographic plotting
import geopandas as gpd
import contextily as cx
import xyzservices.providers as xyz
# unit conversion
cm = 1/2.54 # for inches-cm conversion
# time manipulation
from datetime import datetime
# data science
import numpy as np
import pandas as pd

# i/o
from pathlib import Path, PosixPath, PurePath

# SETUP #########################################

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Arial",
    "font.sans-serif": "Computer Modern",
    'font.size': 16
})

# DATA IMPORT ###################################

countries = gpd.read_file('../_geodata/ne_10m_admin_0_countries')
water = gpd.read_file('../_geodata/ne_10m_rivers_lake_centerlines')
urban = gpd.read_file('../_geodata/ne_10m_urban_areas')
graticules = gpd.read_file('../_geodata/ne_50m_graticules_10')
admin = gpd.read_file('../_geodata/ne_10m_admin_0_countries')
oceans = gpd.read_file('../_geodata/ne_10m_ocean')

proposed_route = gpd.read_file('data/proposed_routes/USA_real.shp')

# https://stackoverflow.com/a/72266527/
path_calculated_route = Path('./data/routes_detailed_slopes/USA')
calculated_route = gpd.GeoDataFrame(
    pd.concat(
        [gpd.read_file(i).to_crs('EPSG:4326')
         for i in path_calculated_route.iterdir()
         if i.suffix == '.shp'
        ],
        ignore_index=True,
    ),
    crs='EPSG:4326'
)

# GEOGRAPHY SETUP ###############################

# https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.set_crs.html
target_projection = "ESRI:102599" # https://epsg.io/102599

countries = countries.to_crs(target_projection)
water = water.to_crs(target_projection)
urban = urban.to_crs(target_projection)
graticules = graticules.to_crs(target_projection)
admin = admin.to_crs(target_projection)
oceans = oceans.to_crs(target_projection)
proposed_route = proposed_route.to_crs(target_projection)
calculated_route = calculated_route.to_crs(target_projection)

# https://geopandas.org/en/stable/docs/reference/api/geopandas.points_from_xy.html#geopandas-points-from-xy
# coordinated can best be selected at:
# https://epsg.io/map
lower_left = gpd.points_from_xy(
    x = [-123.354492], # longitude
    y = [33], # latitude
    crs='EPSG:4326' # = WGS 84
).to_crs(target_projection)
upper_right = gpd.points_from_xy(
    x = [-116], # longitude
    y = [38.151837], # latitude
    crs='EPSG:4326' # = WGS 84
).to_crs(target_projection)

# DATA MANIPULATION #############################

# FIGURE ########################################

# SETUP ######################

fig, ax = plt.subplots(
    num = 'main',
    nrows = 1,
    ncols = 1,
    dpi = 500,
    figsize=(10*cm, 10*cm), # A4=(210x297)mm,
)


urban.plot(
    ax = ax,
    color = 'orange',
    alpha = 1,
)
water.plot(
    ax = ax,
    color = 'lightblue',
    linewidth = 0.75,
    alpha = 1,
)
countries.plot(
    ax = ax,
    facecolor = 'none', # must be "none" instead of None, https://stackoverflow.com/a/47847586
    edgecolor = 'black',
    alpha = 1,
    linewidth = 0.5,
)

# DATA #######################

# AXIS LIMITS ################

ax.set_xlim(
    lower_left.x[0],
    upper_right.x[0]
)

ax.set_ylim(
    lower_left.y[0],
    upper_right.y[0]
)

# TICKS AND LABELS ###########

ax.set_xticks([])
ax.set_yticks([])
ax.set_xticklabels([])
ax.set_yticklabels([])

# GRIDS ######################

# AXIS LABELS ################

# PLOTTING ###################

calculated_route.plot(
    ax = ax,
    color = 'black',
    linewidth = 1.5,
    alpha = 1,
    label = 'Calculated'
)
proposed_route.plot(
    ax = ax,
    color = 'red',
    linewidth = 1.5,
    alpha = 1,
    label = 'Proposed'
)

# MAP BACKGROUND #############

# https://contextily.readthedocs.io/en/latest/working_with_local_files.html#Reading-with-add_basemap
cx.add_basemap(
    ax,
    source='../_geodata/GRAY_HR_SR_W/GRAY_HR_SR_W.tif',
    crs=target_projection
)
# alternatively, tiles could be downloaded from different providers
# using the xyzservices library
# https://geopandas.org/en/stable/gallery/plotting_basemap_background.html#Adding-a-background-map-to-plots

# LEGEND #####################

ax.legend(
    loc = 'lower left',
    fontsize = 16,
    frameon = False,
)

# https://github.com/ppinard/matplotlib-scalebar?tab=readme-ov-file#scalebar-arguments
from matplotlib_scalebar.scalebar import ScaleBar
ax.add_artist(
    ScaleBar(
        dx=1,
        location='lower right',
        box_alpha=0.5,
    )
)

# EXPORT #########################################

path_current_directory: PosixPath = Path(__file__).parent
path_figure: PosixPath = path_current_directory / (Path(__file__).stem + '.png')

plt.savefig(
    fname = path_figure,
    format="png",
    bbox_inches='tight',
    transparent = False
)