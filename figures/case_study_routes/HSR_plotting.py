import plotly.graph_objects as go
import geopandas as gpd

# Mapbox access token
mapbox_access_token = 'YOUR_MAPBOX_KEY'

countries = ['USA', 'Australia', 'Nigeria']
shapefiles = {
    'Nigeria': ['data/Routes_noSlopes/Nigeria.shp'],
    'USA': ['data/real_routes/USA_real.shp'] + [f'data/routes_detailed_slopes/USA/USA_{i}.shp' for i in range(8)],
    'Australia': ['data/real_routes/Australia_real.shp'] + [f'data/routes_detailed_slopes/Australia/Australia_{i}.shp' for i in range(5)]
}
colors = {
    'USA': ['red', 'blue'],
    'Australia': ['red', 'blue'],
    'Nigeria': ['blue']
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

    for idx, shapefile_path in enumerate(shapefiles[country]):
        route_shapefile = gpd.read_file(shapefile_path)
        for index, route in route_shapefile.iterrows():
            if route['geometry'].geom_type == 'LineString':
                coordinates = list(route['geometry'].coords)
                lon, lat = zip(*coordinates)

                color = colors[country][0] if idx == 0 else colors[country][1]  # Use different colors for real and detailed slopes

                fig.add_trace(go.Scattermapbox(
                    lon=list(lon),
                    lat=list(lat),
                    mode='lines',
                    line=dict(width=2, color=color),
                    name=f"{country} Route {idx + 1}"
                ))

                if country == 'Nigeria':
                    fig.add_trace(go.Scattermapbox(
                        lon=[lon[0]],
                        lat=[lat[0]],
                        text=[cities[country][0]],
                        mode='markers+text',
                        marker=dict(size=5, color=color),
                        showlegend=False,
                        textposition='top center',
                        textfont=dict(size=15)
                    ))

                    fig.add_trace(go.Scattermapbox(
                        lon=[lon[-1]],
                        lat=[lat[-1]],
                        text=[cities[country][1]],
                        mode='markers+text',
                        marker=dict(size=5, color=color),
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
