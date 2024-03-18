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

# Define a custom date parser function to handle dates in the 'YYYY/MM' format


def convert_date_from_yyyymm(date_str):
    return pd.to_datetime(date_str, format = '%Y/%m')


def convert_date_from_yyyy(date_str):
    return pd.to_datetime(date_str, format = '%Y')


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
    io = 'data/data.xlsx',
    sheet_name = 'Airbus (2023)',
    parse_dates = ['year'],
    date_parser = convert_date_from_yyyy,
    usecols = lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header = 0,
    engine = 'openpyxl'
)

df_boeing = pd.read_excel(
    io = 'data/data.xlsx',
    sheet_name = 'Boeing (2023)',
    parse_dates = ['year'],
    date_parser = convert_date_from_yyyy,
    usecols = lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header = 0,
    engine = 'openpyxl'
)

df_bain = pd.read_excel(
    io = 'data/data.xlsx',
    sheet_name = 'Bain & Company (2023)',
    parse_dates = ['year'],
    date_parser = convert_date_from_yyyy,
    usecols = lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header = 0,
    engine = 'openpyxl'
)

df_atag = pd.read_excel(
    io = 'data/data.xlsx',
    sheet_name = 'ATAG (2021)',
    parse_dates = ['year'],
    date_parser = convert_date_from_yyyy,
    usecols = lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header = 0,
    engine = 'openpyxl'
)


df_ati = pd.read_excel(
    io = 'data/data.xlsx',
    sheet_name = 'ATI - FlyZero (2022)',
    parse_dates = ['year'],
    date_parser = convert_date_from_yyyy,
    usecols = lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header = 0,
    engine = 'openpyxl'
)

df_JADC = pd.read_excel(
    io = 'data/data.xlsx',
    sheet_name = ' JADC (2022)',
    parse_dates = ['year'],
    date_parser = convert_date_from_yyyy,
    usecols = lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header = 0,
    engine = 'openpyxl'
)

df_ICCT = pd.read_excel(
    io = 'data/data.xlsx',
    sheet_name = 'ICCT (2022)',
    parse_dates = ['year'],
    date_parser = convert_date_from_yyyy,
    usecols = lambda column: column in [
        'year',
        'traffic [RPK]',
    ],
    header = 0,
    engine = 'openpyxl'
)

df_real = pd.read_excel(
    io = 'data/data.xlsx',
    sheet_name = 'Real numbers IATA',
    parse_dates = ['year_month'],
    date_parser = convert_date_from_yyyymm,
    usecols = lambda column: column in [
        'year_month',
        'traffic [RPK]',
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
        figsize = (30*cm, 10*cm),  # A4 = (210x297)mm,
    )

# AXIS LIMITS ################

plt.xlim(pd.Timestamp('2018-01-01'), pd.Timestamp('2050-01-01'))
# ax.set_ylim(0,110)

# TICKS AND LABELS ###########

ax.minorticks_on()
ax.tick_params(axis = 'x', which = 'both', bottom = False)
ax.tick_params(axis = 'y', which = 'both', bottom = False)

# GRIDS ######################

ax.grid(which = 'both', axis = 'y', linestyle = '-', linewidth = 0.5)
ax.grid(which = 'major', axis = 'x', linestyle = '--', linewidth = 0.5)

# AXIS LABELS ################

ax.set_ylabel("Traffic [RPK]")

# PLOTTING ###################

ax.plot(
    df_airbus['year'],
    df_airbus['traffic [RPK]'],
    color = 'black',
    linewidth = 1,
    label = 'Airbus (2023)'
)

ax.plot(
    df_boeing['year'],
    df_boeing['traffic [RPK]'],
    color = 'yellow',
    linewidth = 1,
    label = 'Boeing (2023)'
)

ax.plot(
    df_bain['year'],
    df_bain['traffic [RPK]'],
    color = 'blue',
    linewidth = 1,
    label = 'Bain (2023)'
)

ax.plot(
    df_atag['year'],
    df_atag['traffic [RPK]'],
    color = 'green',
    linewidth = 1,
    label = 'ATAG (2021)'
)

ax.plot(
    df_ati['year'],
    df_ati['traffic [RPK]'],
    color = 'orange',
    linewidth = 1,
    label = 'ATI (2022)'
)

ax.plot(
    df_JADC['year'],
    df_JADC['traffic [RPK]'],
    color = 'pink',
    linewidth = 1,
    label = 'JADC (2022)'
)

ax.plot(
    df_ICCT['year'],
    df_ICCT['traffic [RPK]'],
    color = 'cyan',
    linewidth = 1,
    label = 'ICCT (2022)'
)

ax.plot(
    df_real['year_month'],
    df_real['traffic [RPK]'],
    color = 'red',
    linestyle = '-.',
    linewidth = 1,
    label = 'Real numbers IATA (2023)'
)

# LEGEND ####################

ax.legend(
    loc = 'upper left',
    bbox_to_anchor = (1.05, 1),
    borderaxespad = 0
)


# EXPORT #########################################

file_path = os.path.abspath(__file__)
file_name = os.path.splitext(os.path.basename(file_path))[0]
figure_name: str = str(file_name + '.pdf')

plt.savefig(
    fname = figure_name,
    format = "pdf",
    bbox_inches = 'tight',
    transparent = False
)
