import panel as pn
import plotly.express as px
import forecast_display
from forecast_display import get_scaling_factors, get_sparse_value, df, most_flown_model
from route_view import fig, add_airport_marker_departure, add_airport_marker_destination, reset_map
import airport_check
from general_numbers import General_numbers_df, top_25_airports_df, top_25_connections_df
from country_view import create_country_map, create_continent_map, country_map, create_pie_chart_continent, create_pie_chart_country
from country_comparison import comparison_map, get_unique_departure_countires, add_flight_routes
from world_view import create_connections
import pandas as pd
import plotly.graph_objects as go
import json
import os

pn.extension('plotly', 'vega')

# Load the country-coord.csv file
country_coord_df = pd.read_csv('data/country-coord.csv', index_col=0)

# Load the CountryCodes.json file
with open('data/CountryCodes.json') as json_file:
    country_codes = json.load(json_file)

# Load the Available_Airports.json file
available_airports_path = os.path.join('..', 'api_aerodatabox', 'airport_data', 'Available_Airports.json')
with open(available_airports_path) as json_file:
    available_airports = json.load(json_file)

# Function to get ICAO codes
def get_icao_codes(country_name):
    # Get the Alpha-3 code for the given country
    alpha_3_code = country_coord_df.loc[country_name, 'Alpha-3 code']
    
    # Get the ICAO codes that correspond to this Alpha-3 code
    icao_codes = [key for key, value in country_codes.items() if value == alpha_3_code]
    
    return icao_codes

# Function to find all ICAO codes that start with the given two-letter codes
def find_matching_icao_codes(two_letter_codes):
    matching_icao_codes = []
    print(f"Two-letter codes to match: {two_letter_codes}")  # Debugging line

    for icao_code in available_airports['items']:
        print(f"Checking ICAO code: {icao_code}")  # Debugging line
        if icao_code[:2] in two_letter_codes:
            print(f"Match found: {icao_code}")  # Debugging line
            matching_icao_codes.append(icao_code)

    return matching_icao_codes



# Function to display ICAO codes for a selected country
def display_icao_codes(event):
    country_name = event.new
    if country_name in country_coord_df.index:
        two_letter_codes = get_icao_codes(country_name)
        print(f"Two-letter ICAO codes for {country_name}: {', '.join(two_letter_codes)}")
        matching_icao_codes = find_matching_icao_codes(two_letter_codes)
        print(f"Matching ICAO codes: {', '.join(matching_icao_codes)}")
    else:
        print(f"No Alpha-3 code found for {country_name}")

         

# Define CSS class for border styling and other styles
raw_css = """
div.panel-column {
    border: 2px solid black;
}
"""

TEXT_INPUT_CSS = """
:host(.validation-error) input.bk-input {
    border-color: red !important;  /* Red border for validation error */
    background-color: rgba(255, 0, 0, 0.3) !important;  /* Red background with transparency for validation error */
}
:host(.validation-success) input.bk-input {
    border-color: green !important;  /* Green border for validation success */
}
"""

trip_indicator = pn.widgets.Select(
    name='Legs',
    options=['One-way', 'Round-trip'],
    width=100,
)

time_of_year = pn.widgets.Select(
    name='Timeframe',
    options=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Whole year'],
    width=100,
)

load_factor = pn.widgets.FloatSlider(
    name='Load Factor',
    start=0.0,
    end=1.0,
    step=0.01,
    value=0.8,
    width=200
)

# Create a Panel pane for the Plotly line graph
line_fig = px.line(df,
                   x='Year',
                   y='PAX',
                   markers=True)

line_graph_pane = pn.pane.Plotly(line_fig,
                                 margin = 0,
                                 height=700)

dataframe_pane = pn.pane.DataFrame(df,
                                   sizing_mode="stretch_both", 
                                   max_height=700,
                                   index=False)

# Create the Reset button
reset_button = pn.widgets.Button(name='Reset Data',
                                 button_type='primary',
                                 width=100)

# Create the Reset button
reset_button_LF = pn.widgets.Button(name='Reset LF',
                                 button_type='primary',
                                 width=100)

# Create the Add Route button
add_route_button = pn.widgets.Button(name='Add Route',
                                     button_type='success',
                                     width=100)

number_of_airports = pn.indicators.Number(name='Total airports covered',
                                          value=General_numbers_df["numbers"].iloc[0],
                                          format='{value}')

number_of_connections = pn.indicators.Number(name='Total different connections',
                                             value=General_numbers_df["numbers"].iloc[1],
                                             format='{value}')

number_of_flights = pn.indicators.Number(name='Total flights per year',
                                         value=General_numbers_df["numbers"].iloc[2]*365,
                                         format='{value}')

biggest_airports = pn.pane.DataFrame(top_25_airports_df,
                                     justify="center",
                                     sizing_mode="stretch_both",
                                     max_height=500,
                                     index=False)

biggest_connections = pn.pane.DataFrame(top_25_connections_df,
                                        justify="center",
                                        sizing_mode="stretch_both",
                                        max_height=500,
                                        index=False)

continent_or_country = pn.widgets.Select(name='View',
                                         options=['Continent', 'Country'],
                                         height=100)

departures = get_unique_departure_countires()
country_selection = pn.widgets.AutocompleteInput(name='Select country',
                                                 options=departures,
                                                 case_sensitive=False,
                                                 search_strategy='starts_with',
                                                 placeholder='Write country here',
                                                 min_characters=1)

# Adding display_icao_codes function to be called when country_selection changes
country_selection.param.watch(display_icao_codes, 'value')

# Define the callback function to reset the slider's value
def reset_load_factor(event):
    load_factor.value = 0.8

# Attach the callback to the button's on_click event
reset_button_LF.on_click(reset_load_factor)

# Function to create new route input widgets
def create_route_inputs(route_number):
    icao_departure_input = pn.widgets.TextInput(
        value='',
        placeholder='ICAO code',
        name=f"Departure {route_number}",
        width=100,
        stylesheets=[TEXT_INPUT_CSS]
    )

    icao_destination_input = pn.widgets.TextInput(
        value='',
        placeholder='ICAO code',
        name=f"Destination {route_number}",
        width=100,
        stylesheets=[TEXT_INPUT_CSS]
    )

    return icao_departure_input, icao_destination_input

def create_route_df(departure_input, destination_input):
    df = pd.DataFrame({
            'Year': list(range(2024, 2051)),
            'Seats': [0.0] * 27,
            'Percentage Change': [0.0] * 27,  # Initialize percentage change column
            'PAX': [0.0] * 27  # Initialize PAX column
        })

    @pn.depends(departure_input.param.value, destination_input.param.value, watch=True)
    def update_seats(departure_input, destination_input):
        # Set the time_of_year in the forecast_display module
        global final_df, icao, aircraft_type_df_pane

        # Retrieve current values of other parameters
        load_factor_value = load_factor.value
        time_of_year_value = time_of_year.value
        trip_indicator_value = trip_indicator.value

        forecast_display.set_time_of_year(time_of_year_value)
        scaling_factors = get_scaling_factors(departure_input)
        value = get_sparse_value(departure_input, destination_input, time_of_year_value, trip_indicator_value)

        if value is not None:
            df.at[0, 'Seats'] = round(float(value), 2)  # Explicitly cast to float and round to 2 decimal places
            df.at[0, 'PAX'] = round(float(value) * float(load_factor_value), 2)  # Explicitly cast to float and round to 2 decimal places

        if scaling_factors:
            for i in range(1, len(df)):
                if i < len(scaling_factors):
                    scaling_factor = scaling_factors[i - 1]
                else:
                    scaling_factor = scaling_factors[-1]

                df.at[i, 'Seats'] = round(df.at[i - 1, 'Seats'] * (1 + float(scaling_factor)), 2)  # Explicitly cast to float and round to 2 decimal places
                df.at[i, 'PAX'] = round(df.at[i, 'Seats'] * float(load_factor_value), 2)  # Explicitly cast to float and round to 2 decimal places

                # Calculate percentage change
                prev_seats = df.at[i - 1, 'Seats']
                current_seats = df.at[i, 'Seats']
                if prev_seats != 0:
                    percentage_change = ((current_seats - prev_seats) / prev_seats) * 100
                    df.at[i, 'Percentage Change'] = round(percentage_change, 2)
                else:
                    df.at[i, 'Percentage Change'] = 0.0

        if departure_input != "" and destination_input != "":
            icao.append(departure_input)
            icao.append(destination_input)

        # Update the aircraft type DataFrame only if both ICAO codes are present
        if departure_input and destination_input:
            most_used_model = most_flown_model(departure_input, destination_input)
            aircraft_type_df.at[f"{departure_input}-{destination_input}", 'Most Used Aircraft Type'] = most_used_model
            aircraft_type_df_pane.object = aircraft_type_df.style.set_table_styles(
                [{'selector': 'th', 'props': [('text-align', 'center')]}]
            ).set_properties(**{'text-align': 'center'})

    return df

# Create initial route inputs
route_inputs = [create_route_inputs(1)]

# Create initial dataframe
initial_departure, initial_destination = route_inputs[0]
final_df = create_route_df(initial_departure, initial_destination)

icao = []

# Initialize the aircraft type DataFrame
aircraft_type_df = pd.DataFrame(columns=['Most Used Aircraft Type'])
aircraft_type_df_pane = pn.pane.DataFrame(aircraft_type_df, width=400)

def initial_update_graph(departure_value, destination_value):
    global final_df, line_fig, line_graph_pane, dataframe_pane
    if departure_value and destination_value:  # Ensure both inputs have values
        # Clear existing traces before adding new ones
        line_fig.data = []  # Clear existing figure           

        # Add new traces for each PAX column
        for col in final_df.columns:
            if col.startswith('PAX'):
                line_fig.add_trace(go.Scatter(x=final_df['Year'],
                                              y=final_df['PAX'],
                                              mode='lines+markers',
                                              name=f'Connection: {icao[0]} - {icao[1]}'))

        # Update the line graph pane with the updated line_fig
        line_graph_pane.object = line_fig

        # Update the DataFrame pane with the updated DataFrame
        styled_data = pn.widgets.DataFrame(final_df, name='DataFrame', autosize_mode='fit_columns', height=400, width=300)
        dataframe_pane.object = styled_data

        # Update the aircraft type DataFrame only if both ICAO codes are present
        if departure_value and destination_value:
            most_used_model = most_flown_model(departure_value, destination_value)
            aircraft_type_df.at[f"{departure_value}-{destination_value}", 'Most Used Aircraft Type'] = most_used_model
            aircraft_type_df_pane.object = aircraft_type_df.style.set_table_styles(
                [{'selector': 'th', 'props': [('text-align', 'center')]}]
            ).set_properties(**{'text-align': 'center'})

# Use pn.depends to make update_final_df reactive
pn.depends(initial_departure.param.value, initial_destination.param.value, watch=True)(initial_update_graph)

# Define the callback function to reset the inputs and clear the map
def reset_inputs(event):
    global route_inputs, final_df, icao, aircraft_type_df
    # Reset the initial inputs
    for departure_input, destination_input in route_inputs:
        departure_input.value = ''
        destination_input.value = ''
    # Reset the map and the dataframe
    reset_map()
    icao = []
    final_df = pd.DataFrame({
        'Year': list(range(2024, 2051)),
        'Seats': [0] * 27,
        'Percentage Change': [0.0] * 27,  # Initialize percentage change column
        'PAX': [0] * 27  # Initialize PAX column
    })
    styled_data = pn.widgets.DataFrame(final_df, name='DataFrame', autosize_mode='fit_columns', height=400, width=300)
    dataframe_pane.object = styled_data
    line_graph_pane.object = px.line(final_df, x='Year', y='PAX', markers=True)
    # Keep only the initial route input fields
    route_inputs = [create_route_inputs(1)]
    route_input_column[:] = [pn.Row(*route_inputs[0])]

    add_validation_callbacks(*route_inputs[0])
    initial_departure, initial_destination = route_inputs[0]
    final_df = create_route_df(initial_departure, initial_destination)
    pn.depends(initial_departure.param.value, initial_destination.param.value, watch=True)(initial_update_graph)

    # Reset the aircraft type DataFrame
    aircraft_type_df = pd.DataFrame(columns=['Most Used Aircraft Type'])
    aircraft_type_df_pane.object = aircraft_type_df.style.set_table_styles(
        [{'selector': 'th', 'props': [('text-align', 'center')]}]
    ).set_properties(**{'text-align': 'center'})

reset_button.on_click(reset_inputs)

# Function to add new route inputs
def add_route(event):
    global route_input, final_df, line_graph_pane, line_fig, aircraft_type_df, aircraft_type_df_pane
    route_number = len(route_inputs) + 1
    new_departure_input, new_destination_input = create_route_inputs(route_number)
    route_inputs.append((new_departure_input, new_destination_input))

    route_input_column.append(pn.Row(new_departure_input, new_destination_input))
    add_validation_callbacks(new_departure_input, new_destination_input)
    new_df = create_route_df(new_departure_input, new_destination_input)
    # Define the function to merge new_df into final_df
    def update_final_df(dep_value, dest_value):
        global final_df, icao
        if dep_value and dest_value:  # Ensure both inputs have values
            if not new_df.drop(columns='Year').eq(0).all().all():
                suffixes = ('', f'_{route_number}')
                final_df = pd.merge(final_df, new_df, on='Year', how='left', suffixes=suffixes)
                
                line_fig.data = [] 
                count = 0
                count_1 = 1
                for col in final_df.columns:
                    if col.startswith('PAX'):
                        line_fig.add_trace(go.Scatter(
                            x=final_df['Year'], 
                            y=final_df[col],
                            mode='lines+markers', 
                            name=f'Connection {count_1}: {icao[count]} - {icao[count+1]}'
                        ))
                        count += 2
                        count_1 += 1
                
                line_fig.update_layout(
                    legend=dict(
                        orientation="h",  
                        yanchor="middle",  
                        y=-0.2,  
                        xanchor="center",  
                        x=0.5  
                    )
                )
                
                styled_data = pn.widgets.DataFrame(final_df, name='DataFrame', autosize_mode='fit_columns', height=400, width=300)
                dataframe_pane.object = styled_data

                # Update the aircraft type DataFrame only if both ICAO codes are present
                if dep_value and dest_value:
                    most_used_model = most_flown_model(dep_value, dest_value)
                    aircraft_type_df.at[f"{dep_value}-{dest_value}", 'Most Used Aircraft Type'] = most_used_model
                    aircraft_type_df_pane.object = aircraft_type_df.style.set_table_styles(
                        [{'selector': 'th', 'props': [('text-align', 'center')]}]
                    ).set_properties(**{'text-align': 'center'})

    pn.depends(new_departure_input.param.value, new_destination_input.param.value, watch=True)(update_final_df)

add_route_button.on_click(add_route)

# Callback to validate and update departure marker on input change
def create_validate_departure_callback(departure_input):
    @pn.depends(departure_input.param.value, watch=True)
    def validate_departure(value):
        if airport_check.ICAO_check(value):
            departure_input.css_classes = ["validation-success"]
            add_airport_marker_departure(value)
        else:
            departure_input.css_classes = ["validation-error"]
    return validate_departure

# Callback to validate and update destination marker on input change
def create_validate_destination_callback(destination_input):
    @pn.depends(destination_input.param.value, watch=True)
    def validate_destination(value):
        if airport_check.ICAO_check(value):
            destination_input.css_classes = ["validation-success"]
            add_airport_marker_destination(value)
        else:
            destination_input.css_classes = ["validation-error"]
    return validate_destination

# Function to add validation callbacks for a route
def add_validation_callbacks(departure_input, destination_input):
    create_validate_departure_callback(departure_input)
    create_validate_destination_callback(destination_input)

# Add validation callbacks for the initial route
add_validation_callbacks(*route_inputs[0])

# Initialize route_input_column as an empty pn.Column
route_input_column = pn.Column()
route_input_column[:] = [pn.Row(*route_inputs[0])]

create_continent_map()
@pn.depends(continent_or_country.param.value, watch=True)
def count_or_con(value):
    if value == 'Continent':
        create_continent_map()
    else: 
        create_country_map()

@pn.depends(country_selection.param.value, watch=True)
def country_view(value):
    add_flight_routes(value)

fig2 = create_connections()
pie_chart_1 = create_pie_chart_continent()
pie_chart_2 = create_pie_chart_country()

map_pane = pn.pane.Plotly(fig, css_classes=['panel-column'])
map_pane2 = pn.pane.Plotly(fig2, css_classes=['panel-column'])
comparison_map = pn.pane.Plotly(comparison_map, css_classes=['panel-column'])
country_map = pn.pane.Plotly(country_map, css_classes=['panel-column'])
pie_pane = pn.pane.Plotly(pie_chart_1)
pie_pane2 = pn.pane.Plotly(pie_chart_2)

# Create a column for the slider and button
load_factor_column = pn.Column(load_factor, reset_button_LF, sizing_mode='stretch_width')

# Create the layout for the "Route View" page
route_view_layout = pn.GridSpec(name='Route View', sizing_mode='stretch_both', mode='override')
route_view_layout[0:1, 0:21] = pn.Row(
    trip_indicator,
    time_of_year,
    load_factor_column,
    add_route_button,
    reset_button,
    sizing_mode='stretch_width'
)
route_view_layout[1:6, 0:34] = map_pane
route_view_layout[6:11, 0:15] = dataframe_pane
route_view_layout[6:11, 15:40] = line_graph_pane
route_view_layout[0:1, 33:40] = route_input_column
route_view_layout[11:17,0:35] = aircraft_type_df_pane

# Define pages
pages = {
    "World View": pn.GridSpec(name='World View', sizing_mode='stretch_both', mode='override'),
    "Country View": pn.GridSpec(name='Country View', sizing_mode='stretch_both', mode='override'),
    "Country Comparison": pn.GridSpec(name='Country Comparison', sizing_mode='stretch_both', mode='override'),
    "Route View": route_view_layout,
}

def show(page):
    if page == "World View":
        pages[page][0:2, 0:10] = pn.Column(
            "<h1><u>General Numbers</u></h1>",
            pn.Row(
                pn.Column(number_of_airports, sizing_mode='stretch_width'),
                pn.Column(number_of_connections, sizing_mode='stretch_width'),
                pn.Column(number_of_flights, sizing_mode='stretch_width')
            )
        )
        pages[page][2:9, 0:10] = map_pane2
        pages[page][9:13, 0:5] = pn.Column("<h2><u>List of busiest airports by departing flights</u></h2>", biggest_airports)
        pages[page][9:13, 5:10] = pn.Column("<h2><u> List of busiest flight routes</u></h2>", biggest_connections)
    elif page == "Country View":
        pages[page][0:1, 0:1] = continent_or_country
        pages[page][1:7, 0:10] = country_map
        pages[page][7:13, 0:5] = pie_pane
        pages[page][7:13, 5:10] = pie_pane2
    elif page == "Country Comparison":
        pages[page][0:1, 0:2] = country_selection
        pages[page][1:2, 0:2] = pn.Spacer()  # Placeholder for future elements
        pages[page][2:7, 0:] = comparison_map
        pages[page][8:13, 0:10] = pn.Spacer()
    return pages[page]

starting_page = pn.state.session_args.get("page", [b"World View"])[0].decode()

page = pn.widgets.RadioButtonGroup(
    value=starting_page,
    options=list(pages.keys()),
    name="Page",
    button_type="default",
    orientation='vertical'
)

page.css_classes = ['vertical-radio-buttons']

ishow = pn.bind(show, page=page)
pn.state.location.sync(page, {"value": "page"})

sidebar = pn.Column()
main_layout = pn.Column()

template = pn.template.FastGridTemplate(
    title="Aviation Forecast",
    accent_base_color="#3f51b5",
    header_background="#3f51b5",
    sidebar=[],
    main=main_layout,
    theme='dark',
    theme_toggle=True,
    row_height=100,
)

template.sidebar.append(page)
template.main[:13, :] = ishow

template.servable()
