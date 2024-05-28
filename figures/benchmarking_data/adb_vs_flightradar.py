#%%
# runs code as interactive cell 
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

# plotting
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
# time manipulation
from datetime import datetime
# data science
import numpy as np
import pandas as pd
# i/o
from pathlib import Path, PosixPath, PurePath

# SETUP #########################################

# unit conversion
cm = 1/2.54 # for inches-cm conversion

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Arial",
    "font.sans-serif": "Computer Modern",
    'font.size': 16
})

# DATA IMPORT ###################################

df_adb = pd.read_excel(
    io = 'data/data.xlsx',
    sheet_name = 'ADB',
    parse_dates=['DateTime'],
    usecols = lambda column: column in [
        'DateTime',
        'Flights'
    ],
    header = 0,
    engine = 'openpyxl'
)

df_fr = pd.read_excel(
    io = 'data/data.xlsx',
    sheet_name = 'Flightradar',
    parse_dates=['DateTime'],
    usecols = lambda column: column in [
        'DateTime',
        'Flights'
    ],
    header = 0,
    engine = 'openpyxl'
)

# DATA MANIPULATION #############################

df_fr_pax_only = df_fr.copy()
df_fr_pax_only['Flights'] = df_fr_pax_only['Flights'] - df_fr_pax_only['Flights'] * 0.1
# https://www.eurocontrol.int/publication/eurocontrol-data-snapshot-all-cargo-flights-market-share
# https://aviation.stackexchange.com/a/31988/

# FIGURE ########################################

# SETUP ######################

fig, ax = plt.subplots(
    num = 'main',
    nrows = 1,
    ncols = 1,
    dpi = 300,
    figsize=(30*cm, 10*cm), # A4=(210x297)mm,
)

# AXIS SCALING ###############

# AXIS LIMITS ################

ax.set_xlim(pd.Timestamp('2023-05-01'), pd.Timestamp('2024-04-30'))
ax.set_ylim(0, 140000)

# TICKS AND LABELS ###########

import matplotlib.ticker as ticker
def thousand_formatter(value, tick_number):
    """
    Formats the tick label with thousand separators: 1000 = 1'000.
    """
    return f"{int(value):,}".replace(",", "'")

ax.yaxis.set_major_formatter(ticker.FuncFormatter(thousand_formatter))

ax.tick_params(axis="x",direction="in", pad=-70)
plt.xticks(rotation=90)

x_ticks = ax.xaxis.get_major_ticks()
x_ticks[0].label1.set_visible(False)

# GRIDS ######################

ax.grid(which='both', axis='y', linestyle='-', linewidth = 0.5)
ax.grid(which='both', axis='x', linestyle='-', linewidth = 0.5)

# AXIS LABELS ################

ax.set_ylabel("Global Air Traffic [\# of flights]")

# PLOTTING ###################


ax.plot(
    df_adb['DateTime'],
    df_adb['Flights'],
    color = 'black',
    linestyle = '-',
    linewidth = 1,
    label = 'ADB (our data)'
)
ax.plot(
    df_fr['DateTime'],
    df_fr['Flights'],
    color = 'blue',
    linestyle = '--',
    linewidth = 1,
    label = 'FlightRadar24 (pax + cargo + "some business")'
)
ax.plot(
    df_fr_pax_only['DateTime'],
    df_fr_pax_only['Flights'],
    color = 'blue',
    linestyle = '-.',
    linewidth = 1,
    label = 'FlightRadar24 (pax + "some business")'
)

# LEGEND ####################

ax.legend(
    loc = 'center left',
)

# EXPORT #########################################

path_current_directory: PosixPath = Path(__file__).parent
path_figure: PosixPath = path_current_directory / (Path(__file__).stem + '.pdf')

plt.savefig(
    fname = path_figure,
    format="pdf",
    bbox_inches='tight',
    transparent = False
)