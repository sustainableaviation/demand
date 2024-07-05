import panel as pn
import plotly.express as px
import forecast_display
from forecast_display import get_scaling_factors, get_sparse_value, df
from route_view import fig, add_airport_marker_departure, add_airport_marker_destination
import airport_check
from general_numbers import General_numbers_df, top_25_airports_df, top_25_connections_df
from country_view import create_country_map, create_continent_map, country_map, create_pie_chart_continent, create_pie_chart_country
from country_comparison import comparison_map, get_unique_departure_countires, add_flight_routes
from world_view import create_connections

pn.extension('plotly', 'vega')

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

# TextInput widgets for entering ICAO codes
icao_departure_input = pn.widgets.TextInput(value='',
                                            description="Enter correct departure ICAO code",
                                            placeholder='ICAO code',
                                            name="Departure",
                                            width=100,
                                            stylesheets=[TEXT_INPUT_CSS]
                                            )

icao_destination_input = pn.widgets.TextInput(value='',
                                              description="Enter correct destination ICAO code",
                                              placeholder='ICAO code',
                                              name="Destination",
                                              width=100,
                                              stylesheets=[TEXT_INPUT_CSS]
                                              )

trip_indicator = pn.widgets.Select(name='Legs',
                                   description="Choose between One-way or Round-trip",
                                   options=['One-way', 'Round-trip'],
                                   width=100,
                                   )

time_of_year = pn.widgets.Select(name='Timeframe',
                                 options=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Whole year'],
                                 width=100, )

load_factor = pn.widgets.FloatSlider(name='Load Factor',
                                     start=0.0,
                                     end=1.5,
                                     step=0.01,
                                     value=0.8,
                                     width=200)

# Create a Panel pane for the Plotly line graph
line_fig = px.line(df,
                   x='Year',
                   y='PAX',
                   title='PAX Forecast',
                   markers=True)

line_graph_pane = pn.pane.Plotly(line_fig,
                                 height=700)

dataframe_pane = pn.pane.DataFrame(df,
                                   sizing_mode="stretch_both",
                                   max_height=500,
                                   index=False)

# Create the Reset button
reset_button = pn.widgets.Button(name='Reset LF',
                                 button_type='primary',
                                 width=100)


number_of_airports = pn.indicators.Number(name='Total airports covered', value=General_numbers_df["numbers"].iloc[0], format='{value}')
number_of_connections = pn.indicators.Number(name='Total different connections', value=General_numbers_df["numbers"].iloc[1], format='{value}')
number_of_flights = pn.indicators.Number(name='Total flights per year', value=General_numbers_df["numbers"].iloc[2]*365, format='{value}')

# Select columns to display
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
                                   description="Choose between continent or country view",
                                   options=['Continent', 'Country'],
                                   height=100)

departures = get_unique_departure_countires()
country_selection = pn.widgets.AutocompleteInput(
                                                name='Select country', 
                                                options=departures,
                                                case_sensitive=False, 
                                                search_strategy='starts_with',
                                                placeholder='Write country here',
                                                min_characters = 1)


# Define the callback function to reset the slider's value
def reset_load_factor(event):
    load_factor.value = 0.8


# Attach the callback to the button's on_click event
reset_button.on_click(reset_load_factor)


# Callback to update the Seats value based on ICAO codes
@pn.depends(icao_departure_input.param.value, icao_destination_input.param.value, load_factor.param.value, time_of_year.param.value, trip_indicator.param.value, watch=True)
def update_seats(departure_code, destination_code, load_factor_value, time_of_year_value, trip_indicator_value):
    # Set the time_of_year in the forecast_display module
    forecast_display.set_time_of_year(time_of_year_value)
    scaling_factors = get_scaling_factors(departure_code)
    value = get_sparse_value(departure_code, destination_code, time_of_year_value, trip_indicator_value)

    if value is not None:
        df.at[0, 'Seats'] = value
        df.at[0, 'PAX'] = value * load_factor_value

    if scaling_factors:
        for i in range(1, len(df)):
            if i < len(scaling_factors):
                scaling_factor = scaling_factors[i - 1]
            else:
                scaling_factor = scaling_factors[-1]

            df.at[i, 'Seats'] = df.at[i - 1, 'Seats'] * (1 + scaling_factor)
            df.at[i, 'PAX'] = df.at[i, 'Seats'] * load_factor_value

            # Calculate percentage change
            prev_seats = df.at[i - 1, 'Seats']
            current_seats = df.at[i, 'Seats']
            if prev_seats != 0:
                percentage_change = ((current_seats - prev_seats) / prev_seats) * 100
                df.at[i, 'Percentage Change'] = round(percentage_change, 2)
            else:
                df.at[i, 'Percentage Change'] = 0.0

    # Update the DataFrame and line plot
    styled_data = pn.widgets.DataFrame(df, name='DataFrame', autosize_mode='fit_columns', height=400, width=300)
    dataframe_pane.object = styled_data

    # Update the line graph
    line_fig = px.line(df, x='Year', y='PAX', title='Seats Forecast', markers=True)
    line_graph_pane.object = line_fig


# Callback to validate and update departure marker on input change
@pn.depends(icao_departure_input.param.value, watch=True)
def validate_departure(value):
    if airport_check.ICAO_check(value):
        icao_departure_input.css_classes = ["validation-success"]
        add_airport_marker_departure(value)
    else:
        icao_departure_input.css_classes = ["validation-error"]


# Callback to validate and update destination marker on input change
@pn.depends(icao_destination_input.param.value, watch=True)
def validate_destination(value):
    if airport_check.ICAO_check(value):
        icao_destination_input.css_classes = ["validation-success"]
        add_airport_marker_destination(value)
    else:
        icao_destination_input.css_classes = ["validation-error"]

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

# Define pages
pages = {
    "World View": pn.GridSpec(
        name='World View',
        sizing_mode='stretch_both',
        mode='override'
    ),
    "Country View": pn.GridSpec(
        name='Country View',
        sizing_mode='stretch_both',
        mode='override'
    ),
    "Country Comparison": pn.GridSpec(
        name='Country Comparison',
        sizing_mode='stretch_both',
        mode='override'
    ),
    "Route View": pn.GridSpec(
        name='Route View',
        sizing_mode='stretch_both',
        mode='override'
    ),
}

# Create a column for the slider and button
load_factor_column = pn.Column(load_factor, reset_button, sizing_mode='stretch_width')


# Function to display the selected page
def show(page):
    if page == "World View":
        pages[page][0:2, 0:10] = pn.Column(
            "<h1><u>General Numbers</u></h1>",  # Markdown text
            pn.Row(
                pn.Column(number_of_airports, sizing_mode='stretch_width'),
                pn.Column(number_of_connections, sizing_mode='stretch_width'),
                pn.Column(number_of_flights, sizing_mode='stretch_width')
            )
        )
        pages[page][2:9, 0:10] = map_pane2
        pages[page][9:13, 0:5] = pn.Column(
            "<h2><u>List of busiest airports by departing flights</u></h2>", biggest_airports)
        pages[page][9:13, 5:10] = pn.Column(
            "<h2><u> List of busiest flight routes</u></h2>", biggest_connections)
    elif page == "Route View":
        pages[page][0:1, 0:9] = pn.Row(
            trip_indicator,
            icao_departure_input,
            icao_destination_input,
            time_of_year,
            load_factor_column,
            sizing_mode='stretch_width'
        )
        pages[page][1:8, 0:] = map_pane
        pages[page][8:13, 0:3] = dataframe_pane
        pages[page][8:13, 3:9] = line_graph_pane
    elif page == "Country View":
        pages[page][0:1, 0:1] = continent_or_country
        pages[page][1:7, 0:10] = country_map
        pages[page][7:13, 0:5] = pie_pane
        pages[page][7:13, 5:10] = pie_pane2
    elif page == "Country Comparison":
        pages[page][0:1, 0:2] = country_selection
        pages[page][1:7, 0:] = comparison_map
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

# Apply custom CSS to achieve vertical alignment
page.css_classes = ['vertical-radio-buttons']

ishow = pn.bind(show, page=page)
pn.state.location.sync(page, {"value": "page"})

# Create the sidebar and template
sidebar = pn.Column()

# Define the main layout
main_layout = pn.Column()

# Create the main container
template = pn.template.FastGridTemplate(
    title="Aviation Forecast",
    accent_base_color="#3f51b5",
    header_background="#3f51b5",
    sidebar=[],  # Initialize an empty sidebar
    main=main_layout,
    theme='dark',
    theme_toggle=True,
    row_height=100,
)

# Add the page selector to the sidebar
template.sidebar.append(page)

# Add the selected page to the main area
template.main[:14, :] = ishow

# Serve the template
template.servable()
