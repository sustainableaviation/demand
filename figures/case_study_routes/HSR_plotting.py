import plotly.graph_objects as go
import geopandas as gpd

# Mapbox access token
mapbox_access_token = 'YOUR_MAPBOX_KEY'

countries = ['USA', 'Australia', 'Nigeria']
shapefiles = {
    'USA': 'data/Routes_noSlopes/USA.shp',
    'Australia': 'data/Routes_noSlopes/Australia.shp',
    'Nigeria': 'data/Routes_noSlopes/Nigeria.shp'
}
colors = {
    'USA': 'red',
    'Australia': 'blue',
    'Nigeria': 'blue'
}
cities = {
    'USA': ('', ''),
    'Australia': ('Sydney', 'Melbourne'),
    'Nigeria': ('Abuja', 'Lagos')
}
zooms = {
    'USA': {'center_lon': -120, 'center_lat': 36, 'zoom': 6.5},
    'Australia': {'center_lon': 147, 'center_lat': -36, 'zoom': 6.5},
    'Nigeria': {'center_lon': 5, 'center_lat': 8, 'zoom': 6.5}
}

for country in countries:
    fig = go.Figure()

    route_shapefile = gpd.read_file(shapefiles[country])
    for index, route in route_shapefile.iterrows():
        if route['geometry'].geom_type == 'LineString':
            coordinates = list(route['geometry'].coords)
            lon, lat = zip(*coordinates)

            fig.add_trace(go.Scattermapbox(
                lon=list(lon),
                lat=list(lat),
                mode='lines',
                line=dict(width=2, color=colors[country]),
                name=f"{country} Route"
            ))

            fig.add_trace(go.Scattermapbox(
                lon=[lon[0]],
                lat=[lat[0]],
                text=[cities[country][0]],
                mode='markers+text',
                marker=dict(size=5, color=colors[country]),
                showlegend=False,
                textposition='top center',
                textfont=dict(size=15)
            ))

            fig.add_trace(go.Scattermapbox(
                lon=[lon[-1]],
                lat=[lat[-1]],
                text=[cities[country][1]],
                mode='markers+text',
                marker=dict(size=5, color=colors[country]),
                showlegend=False,
                textposition='bottom center',
                textfont=dict(size=15)
            ))

    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_access_token,
            style='mapbox://styles/mapbox/outdoors-v11',  # Terrain style map
            center=dict(lon=zooms[country]['center_lon'], lat=zooms[country]['center_lat']),
            zoom=zooms[country]['zoom']
        ),
        title=f'Route Overview: {country}'
    )

    # Show the figure
    fig.show()

