#######################################
# IMPORTS #############################
#######################################

import matplotlib.pyplot as plt
import pandas as pd
import sys
from pathlib import Path

# Determine the current directory
current_directory = Path(__file__).resolve().parent

# Add the path to the api_aerodatabox folder to sys.path
api_aerodatabox_path = current_directory.parents[1] / 'api_aerodatabox'
sys.path.insert(0, str(api_aerodatabox_path))

# Now you can import the module
import data_transformation_pandas

# Unit conversion
cm = 1 / 2.54  # for inches-cm conversion

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Arial",
    "font.sans-serif": "Computer Modern",
    'font.size': 12
})


#######################################
# Data import & transformation ########
#######################################

# Define the month list
month_list = ["05-May", "06-June", "07-July", "08-August", "09-September", "10-October", "11-November", "12-December", "01-January", "02-February", "03-March", "04-April"]
month_list_2 = [5.23, 6.23, 7.23, 8.23, 9.23, 10.23, 11.23, 12.23, 1.24, 2.24, 3.24, 4.24]

# Convert float months to datetime objects
month_list_2 = pd.to_datetime(month_list_2, format='%m.%y')

# Initialize a list to store monthly total flights
monthly_total_flights_list = []

# Calculate monthly total flights for each month
for month in month_list:
    flight_data_df, daily_flights_df = data_transformation_pandas.process_flight_connections(month)
    monthly_total_flights = daily_flights_df["number_of_total_flights"].sum()  # Assuming you're scaling to get monthly total
    monthly_total_flights_list.append(monthly_total_flights)

# Initialize a DataFrame to store monthly total flights
monthly_total_flights_df = pd.DataFrame({
    'Month': month_list_2,
    'Total Flights': monthly_total_flights_list
})

# Load real flight data
df_real = pd.read_excel(
    io=current_directory / "FlightRadar_data.xlsx",
    sheet_name='plotting_data',
    parse_dates=['DateTime'],
    usecols=lambda column: column in [
        'DateTime',
        'Number of flights',
    ],
    header=0,
    engine='openpyxl'
)


#######################################
# Plotting ############################
#######################################

# Create a subplot
fig, ax1 = plt.subplots(
    num='main',
    nrows=1,
    ncols=1,
    dpi=300,
    figsize=(30 * cm, 12 * cm),  # A4 = (210x297)mm
)

# Set axis limits and labels
plt.xlim(pd.Timestamp('2023-05-01'), pd.Timestamp('2024-04-30'))
ax1.set_ylim(50000, 150000)
ax1.set_ylabel("Global Air Traffic [flights]")

plt.title("Yearly Distribution of Flights (May 2023 - April 2024)")

# Grids
ax1.grid(which='both', axis='y', linestyle='-', linewidth=0.5)
ax1.grid(which='major', axis='x', linestyle='--', linewidth=0.5)

ax1.set_xticks(month_list_2)  # Set the ticks based on the data
ax1.set_xticklabels(month_list, rotation=45)  # Set the tick labels accordingly

ax1.plot(
    df_real['DateTime'],
    df_real['Number of flights'],
    color='#e41a1c',
    linewidth=1,
    label='Data from flightradar24'
)

ax1.plot(
    monthly_total_flights_df['Month'],
    monthly_total_flights_df['Total Flights'],
    color='#377eb8',
    linewidth=1,
    label='Data from AeroDataBox'
)

ax1.legend(
    loc='upper left',
    fontsize=8,
    borderaxespad=1
)


#######################################
# Export PDF ##########################
#######################################

# Save the plot as a PDF
figure_name = current_directory / "yearly_distribution_of_flights.pdf"

plt.savefig(
    fname=str(figure_name),
    format="pdf",
    bbox_inches='tight',
    transparent=False
)
