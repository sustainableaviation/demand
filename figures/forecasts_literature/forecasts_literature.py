# %%
# runs code as interactive cell
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

# plotting
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# data science
import pandas as pd

# i/o
import os

# SETUP #########################################

# unit conversion
cm = 1/2.54  # for inches-cm conversion

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Arial",
    "font.sans-serif": "Computer Modern",
    'font.size': 16
})

# DATA IMPORT ###################################

def read_traffic_data(sheet_name, parse_dates, engine='openpyxl'):
    return pd.read_excel(
        # io='/Users/barend/Desktop/Thesis/demandmap/figures/forecasts_literature/data/data.xlsx',
        io='data/data.xlsx',
        sheet_name=sheet_name,
        parse_dates=parse_dates,
        usecols=lambda column: column in [
            'year',
            'traffic [RPK]',
        ],
        header=0,
        engine=engine
    )


df_airbus = read_traffic_data('Airbus (2023)', ['year'])
df_boeing = read_traffic_data('Boeing (2023)', ['year'])
df_bain = read_traffic_data('Bain & Company (2023)', ['year'])
df_atag = read_traffic_data('ATAG (2021)', ['year'])
df_ati = read_traffic_data('ATI - FlyZero (2022)', ['year'])
df_jadc = read_traffic_data('JADC (2022)', ['year'])
df_icct = read_traffic_data('ICCT (2022)', ['year'])


df_real = pd.read_excel(
    # io='/Users/barend/Desktop/Thesis/demandmap/figures/forecasts_literature/data/data.xlsx',
    io='data/data.xlsx',
    sheet_name='Real numbers IATA',
    parse_dates=['year_month'],
    date_format='%Y/%m',
    usecols=lambda column: column in [
        'year_month',
        'traffic [RPK]',
    ],
    header=0,
    engine='openpyxl'
)

df_GDP_upper = pd.read_excel(
    #io='/Users/barend/Desktop/Thesis/demandmap/figures/forecasts_literature/data/data.xlsx',
    io='data/data.xlsx',
    sheet_name='GDP upper',
    parse_dates=['year'],
    usecols=lambda column: column in [
        'year',
        'GDP',
    ],
    header=0,
    engine='openpyxl'
)

df_GDP_lower = pd.read_excel(
    #io='/Users/barend/Desktop/Thesis/demandmap/figures/forecasts_literature/data/data.xlsx',
    io='data/data.xlsx',
    sheet_name='GDP lower',
    parse_dates=['year'],
    usecols=lambda column: column in [
        'year',
        'GDP',
    ],
    header=0,
    engine='openpyxl'
)

# DATA MANIPULATION #############################

for df in [
    df_airbus,
    df_boeing,
    df_bain,
    df_atag,
    df_ati,
    df_jadc,
    df_icct,
    df_real
]:
    df['traffic [trillion RPK]'] = df['traffic [RPK]'] / 1e12  # to trillion RPK

# FIGURE ########################################

# SETUP ######################

fig, ax1 = plt.subplots(
        num='main',
        nrows=1,
        ncols=1,
        dpi=300,
        figsize=(30*cm, 12*cm),  # A4 = (210x297)mm,
    )

ax2 = ax1.twinx()  # Create a twin Axes sharing the xaxis

# AXIS LIMITS ################

plt.xlim(pd.Timestamp('2018-01-01'), pd.Timestamp('2050-01-01'))
ax2.set_ylim(0, 400)
ax1.set_ylim(0, 35)

# TICKS AND LABELS ###########

ax1.xaxis.set_major_locator(mdates.YearLocator())
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)

ax1.minorticks_on()
ax1.tick_params(axis='x', which='both', bottom=False)
ax1.tick_params(axis='y', which='both', bottom=False)

# GRIDS ######################

ax1.grid(which='both', axis='y', linestyle='-', linewidth=0.5)
ax1.grid(which='major', axis='x', linestyle='--', linewidth=0.5)

# AXIS LABELS ################

ax1.set_ylabel("Global Passenger Air Traffic [trillion RPK]")
ax2.set_ylabel("World GDP [trillion USD2005]")

# PLOTTING ###################

# Shading the area between GDP upper and lower
ax2.fill_between(
    df_GDP_upper['year'],
    df_GDP_upper['GDP'],
    df_GDP_lower['GDP'],
    color='cyan',  # Adjust the color here
    alpha=0.15  # Adjust the transparency here
)

ax1.plot(
    df_airbus['year'],
    df_airbus['traffic [trillion RPK]'],
    color='#377eb8',
    linewidth=1.5,
    label='Airbus (2023)'
)

ax1.plot(
    df_boeing['year'],
    df_boeing['traffic [trillion RPK]'],
    color='#ff7f00',
    linewidth=1.5,
    label='Boeing (2023)'
)

ax1.plot(
    df_bain['year'],
    df_bain['traffic [trillion RPK]'],
    color='#4daf4a',
    linewidth=1.5,
    label='Bain (2023)'
)

ax1.plot(
    df_atag['year'],
    df_atag['traffic [trillion RPK]'],
    color='#f781bf',
    linewidth=1.5,
    label='ATAG (2021)'
)

ax1.plot(
    df_ati['year'],
    df_ati['traffic [trillion RPK]'],
    color='#a65628',
    linewidth=1.5,
    label='ATI (2022)'
)

ax1.plot(
    df_jadc['year'],
    df_jadc['traffic [trillion RPK]'],
    color='#984ea3',
    linewidth=1.5,
    label='JADC (2022)'
)

ax1.plot(
    df_icct['year'],
    df_icct['traffic [trillion RPK]'],
    color='#999999',
    linewidth=1.5,
    label='ICCT (2022)'
)

ax1.plot(
    df_real['year_month'],
    df_real['traffic [trillion RPK]'],
    color='#e41a1c',
    linestyle='-.',
    linewidth=1.5,
    label='Historical Data'
)

# Plotting GDP upper and lower
ax2.plot(
    df_GDP_upper['year'],
    df_GDP_upper['GDP'],
    color='#377eb8',
    linestyle='--',
    linewidth=1.5,
    label='GDP high growth (IIASA)'
)

ax2.plot(
    df_GDP_lower['year'],
    df_GDP_lower['GDP'],
    color='#ff7f00',
    linestyle='--',
    linewidth=1.5,
    label='GDP low growth (IIASA)'
)

ax1.axvline(
    x=pd.Timestamp('2024'),
    color='black',
    linewidth=1.5,
)

# LEGEND ####################

ax1.legend(
    loc='upper left',
    borderaxespad=1,
    ncol=2
)

ax2.legend(
    loc='lower right',
    borderaxespad=1
)

# EXPORT #########################################

file_path = os.path.abspath(__file__)
file_name = os.path.splitext(os.path.basename(file_path))[0]
figure_name: str = str(file_name + '.pdf')

plt.savefig(
    fname=figure_name,
    format="pdf",
    bbox_inches='tight',
    transparent=False
)

# %%