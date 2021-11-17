# Configuración
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt

# Built-in Python Modules
import datetime
import inspect
import io
import os
import csv
import json
import math
import glob
import pytz
import random
import warnings
import traitlets
from calendar import monthrange
warnings.filterwarnings(action='ignore')

# Widgets
import ipywidgets as widgets
from IPython.display import display

# Complementos de Python
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib as mpl
from functools import reduce
from matplotlib import dates as mpl_dates
from sklearn.metrics import mean_squared_error, r2_score

# Módulos Sandia PVLIB-Python
import pvlib
# from pvlib import solarposition, irradiance, atmosphere, pvsystem
# from pvlib.location import Location
# from pvlib.pvsystem import PVSystem, retrieve_sam

# Warnings
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('numexpr').setLevel(logging.WARNING)

# Scripts
from cnosolar import cell_temperature
from cnosolar import cen
# from cnosolar import complements
from cnosolar import data
from cnosolar import def_pvsystem
from cnosolar import energia_minima
from cnosolar import gui_config
from cnosolar import gui_protocols
from cnosolar import irradiance_models
from cnosolar import location_data
from cnosolar import pipeline
from cnosolar import production
from cnosolar import pvstructure
from cnosolar.pvsyst_tools import pvsyst

if __name__ == '__main__':
    print(f'Successfully executed from {__name__}.')