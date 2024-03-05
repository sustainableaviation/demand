#%%
# runs code as interactive cell 
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

# plotting
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
# unit conversion
cm = 1/2.54 # for inches-cm conversion
# time manipulation
from datetime import datetime

# data science
import numpy as np
import pandas as pd

# i/o
from pathlib import PurePath, Path

# SETUP #########################################


plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Arial",
    "font.sans-serif": "Computer Modern",
    'font.size': 12
})

# DATA IMPORT ###################################

df_airbus = pd.read_excel(
    io = 'data/data.xlsx',
    sheet_name = 'Airbus (2023)',
    usecols = lambda column: column in [
        'year',
        'traffic [Mpax-km]',
    ],
    header = 0,
    engine = 'openpyxl'
)
# DATA MANIPULATION #############################

# FIGURE ########################################

# SETUP ######################

fig, ax = plt.subplots(
        num = 'main',
        nrows = 1,
        ncols = 1,
        dpi = 300,
        figsize=(30*cm, 10*cm), # A4=(210x297)mm,
    )

# AXIS LIMITS ################

ax.set_xlim(2020, 2050)
#ax.set_ylim(0,110)

# TICKS AND LABELS ###########

ax.minorticks_on()
ax.tick_params(axis='x', which='both', bottom=False)
ax.tick_params(axis='y', which='both', bottom=False)

# GRIDS ######################

ax.grid(which='both', axis='y', linestyle='-', linewidth = 0.5)
ax.grid(which='major', axis='x', linestyle='--', linewidth = 0.5)

# AXIS LABELS ################

ax.set_ylabel("Traffic [Mio. pax-km]")

# PLOTTING ###################

ax.plot(
    df_airbus['year'],
    df_airbus['traffic [Mpax-km]'],
    color = 'black',
    linewidth = 1,
    label = 'Airbus (2023)'
)

# LEGEND ####################

ax.legend(
    loc='upper right',
)

# EXPORT #########################################

file_path = os.path.abspath(__file__)
file_name = os.path.splitext(os.path.basename(file_path))[0]
figure_name: str = str(file_name + '.pdf')

plt.savefig(
    fname = figure_name,
    format="pdf",
    bbox_inches='tight',
    transparent = False
)