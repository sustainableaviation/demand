import plotly.graph_objects as go
import geopandas as gpd

# List of countries and their respective shapefiles
countries = ['USA', 'Australia', 'Nigeria']
shapefiles = {
    'USA': 'data/Routes_noSlopes/USA.shp',
    'Australia': 'data/Routes_noSlopes/Australia.shp',
    'Nigeria': 'data/Routes_noSlopes/Nigeria.shp'
}
colors = {
    'USA': 'red',
    'Australia': 'blue',
    'Nigeria': 'green'
}
cities = {
    'USA': ('San Francisco', 'Los Angeles'),
    'Australia': ('Sydney', 'Melbourne'),
    'Nigeria': ('Abuja', 'Lagos')
}
zooms = {
    'USA': {'lonaxis_range': [-124, -114], 'lataxis_range': [32, 40]},  # Approximate bounds for California
    'Australia': {'lonaxis_range': [142, 152], 'lataxis_range': [-39, -33]},  # Approximate bounds for Southeast Australia
    'Nigeria': {'lonaxis_range': [2, 8], 'lataxis_range': [6, 12]}  # Approximate bounds for Western Nigeria
}

# Process each country
for country in countries:
    # Create a new figure
    fig = go.Figure()

    # Load the shapefile
    route_shapefile = gpd.read_file(shapefiles[country])
    for index, route in route_shapefile.iterrows():
        if route['geometry'].geom_type == 'LineString':
            coordinates = list(route['geometry'].coords)
            lon, lat = zip(*coordinates)

            # Add route line
            fig.add_trace(go.Scattergeo(
                lon=list(lon),
                lat=list(lat),
                mode='lines',
                line=dict(width=2, color=colors[country]),
                name=f"{country} Route"
            ))

            # Add start city marker
            fig.add_trace(go.Scattergeo(
                lon=[lon[0]],
                lat=[lat[0]],
                text=[cities[country][0]],
                mode='markers+text',
                marker=dict(size=5, color=colors[country]),
                showlegend=False,
                textposition='top center'
            ))

            # Add end city marker
            fig.add_trace(go.Scattergeo(
                lon=[lon[-1]],
                lat=[lat[-1]],
                text=[cities[country][1]],
                mode='markers+text',
                marker=dict(size=5, color=colors[country]),
                showlegend=False,
                textposition='bottom center'
            ))

    # Update the map layout to focus on the specific country's route
    fig.update_geos(
        projection_type="natural earth",
        showcountries=True,
        lonaxis_range=zooms[country]['lonaxis_range'],
        lataxis_range=zooms[country]['lataxis_range']
    )

    # Set the layout of the map
    fig.update_layout(
        title=f'Route Overview: {country} with Cities',
        geo_scope='world',  # Set scope to world to show all countries
        showlegend=True
    )

    # Show the figure
    fig.show()
