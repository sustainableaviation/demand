#%%
# runs code as interactive cell
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

# plotting
import matplotlib.pyplot as plt
# import matplotlib.font_manager as font_manager

# time manipulation
# from datetime import datetime

# data science
# import numpy as np
import pandas as pd

# i/o
# from pathlib import PurePath, Path
import os

# SETUP #########################################

# unit conversion
cm = 1/2.54  # for inches-cm conversion

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Arial",
    "font.sans-serif": "Computer Modern",
    'font.size': 12
})

# DATA IMPORT ###################################

df_airbus = pd.read_excel(
    io='data/data.xlsx',
    sheet_name='Airbus (2023)',
    parse_dates=['year'],
    usecols=lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header=0,
    engine='openpyxl'
)

df_boeing = pd.read_excel(
    io='data/data.xlsx',
    sheet_name='Boeing (2023)',
    parse_dates=['year'],
    usecols=lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header=0,
    engine='openpyxl'
)

df_bain = pd.read_excel(
    io='data/data.xlsx',
    sheet_name='Bain & Company (2023)',
    parse_dates=['year'],
    usecols=lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header=0,
    engine='openpyxl'
)

df_atag = pd.read_excel(
    io='data/data.xlsx',
    sheet_name='ATAG (2021)',
    parse_dates=['year'],
    usecols=lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header=0,
    engine='openpyxl'
)


df_ati = pd.read_excel(
    io='data/data.xlsx',
    sheet_name='ATI - FlyZero (2022)',
    parse_dates=['year'],
    usecols=lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header=0,
    engine='openpyxl'
)

df_JADC = pd.read_excel(
    io='data/data.xlsx',
    sheet_name=' JADC (2022)',
    parse_dates=['year'],
    usecols=lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header=0,
    engine='openpyxl'
)

df_ICCT = pd.read_excel(
    io='data/data.xlsx',
    sheet_name='ICCT (2022)',
    parse_dates=['year'],
    usecols=lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header=0,
    engine='openpyxl'
)

df_real = pd.read_excel(
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

# DATA MANIPULATION #############################

for df in [
    df_airbus,
    df_boeing,
    df_bain,
    df_atag,
    df_ati,
    df_JADC,
    df_ICCT,
    df_real
]:
    df['traffic [trillion RPK]'] = df['traffic [RPK]'] / 1e12  # to trillion RPK

# FIGURE ########################################

# SETUP ######################

fig, ax = plt.subplots(
        num='main',
        nrows=1,
        ncols=1,
        dpi=300,
        figsize=(30*cm, 10*cm),  # A4 = (210x297)mm,
    )

# AXIS LIMITS ################

plt.xlim(pd.Timestamp('2018-01-01'), pd.Timestamp('2050-01-01'))
# ax.set_ylim(0,110)

# TICKS AND LABELS ###########

import matplotlib.dates as mdates
ax.xaxis.set_major_locator(mdates.YearLocator())
plt.xticks(rotation=90)

ax.minorticks_on()
ax.tick_params(axis='x', which='both', bottom=False)
ax.tick_params(axis='y', which='both', bottom=False)

# GRIDS ######################

ax.grid(which='both', axis='y', linestyle='-', linewidth=0.5)
ax.grid(which='major', axis='x', linestyle='--', linewidth=0.5)

# AXIS LABELS ################

ax.set_ylabel("Global Passenger Air Traffic [trillion RPK]")

# PLOTTING ###################

ax.plot(
    df_airbus['year'],
    df_airbus['traffic [trillion RPK]'],
    color='#377eb8',
    linewidth=1,
    label='Airbus (2023)'
)

ax.plot(
    df_boeing['year'],
    df_boeing['traffic [trillion RPK]'],
    color='#ff7f00',
    linewidth=1,
    label='Boeing (2023)'
)

ax.plot(
    df_bain['year'],
    df_bain['traffic [trillion RPK]'],
    color='#4daf4a',
    linewidth=1,
    label='Bain (2023)'
)

ax.plot(
    df_atag['year'],
    df_atag['traffic [trillion RPK]'],
    color='#f781bf',
    linewidth=1,
    label='ATAG (2021)'
)

ax.plot(
    df_ati['year'],
    df_ati['traffic [trillion RPK]'],
    color='#a65628',
    linewidth=1,
    label='ATI (2022)'
)

ax.plot(
    df_JADC['year'],
    df_JADC['traffic [trillion RPK]'],
    color='#984ea3',
    linewidth=1,
    label='JADC (2022)'
)

ax.plot(
    df_ICCT['year'],
    df_ICCT['traffic [trillion RPK]'],
    color='#999999',
    linewidth=1,
    label='ICCT (2022)'
)

ax.plot(
    df_real['year_month'],
    df_real['traffic [trillion RPK]'],
    color='#e41a1c',
    linestyle='-.',
    linewidth=1,
    label='Real numbers IATA (2023)'
)

ax.axvline(
    x=pd.Timestamp('2024'),
    color='black',
    linewidth=1,
)

# LEGEND ####################

ax.legend(
    loc='lower right',
    fontsize=10,
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
