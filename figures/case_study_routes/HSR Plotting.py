import plotly.graph_objects as go
import geopandas as gpd

# Create a new figure
fig = go.Figure()

# Load the world map data
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))


def plot_geometry(geom, fig, line_color):
    """Handle both Polygon and MultiPolygon geometries for plotting."""
    if geom.geom_type == 'Polygon':
        lon, lat = geom.exterior.xy
        fig.add_trace(go.Scattergeo(
            lon=list(lon),
            lat=list(lat),
            mode='lines',
            line=dict(width=1, color=line_color)
        ))
    elif geom.geom_type == 'MultiPolygon':
        for poly in geom.geoms:
            lon, lat = poly.exterior.xy
            fig.add_trace(go.Scattergeo(
                lon=list(lon),
                lat=list(lat),
                mode='lines',
                line=dict(width=1, color=line_color)
            ))

# Add the world countries as a scattergeo plot
for _, country in world.iterrows():
    plot_geometry(country['geometry'], fig, 'blue')


# Load the shapefile for the route
route_shapefile = gpd.read_file('data/Routes_noSlopes/2 path4_no infrastructure.shp')

# Add the route from the shapefile to the plot
for _, route in route_shapefile.iterrows():
    if route['geometry'].geom_type == 'LineString':
        lon, lat = zip(*list(route['geometry'].coords))
        fig.add_trace(go.Scattergeo(
            lon=list(lon),
            lat=list(lat),
            mode='lines',
            line=dict(width=2, color='red')
        ))

# Update the map layout to focus on Nigeria
fig.update_geos(
    projection_type="natural earth",
    showcountries=False,  # Country outlines already plotted
    lonaxis_range=[2, 14],  # Longitude range for zoom
    lataxis_range=[4, 14]  # Latitude range for zoom
)

# Set the layout of the map
fig.update_layout(
    title='Case Study Lagos-Abuja',
    geo_scope='world',  # Set scope to world to show all countries
)

# Show the figure
fig.show()
