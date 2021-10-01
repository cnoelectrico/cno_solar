#Configuración
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt

#Built-in Python Modules
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
from calendar import monthrange
warnings.filterwarnings(action='ignore')

#Widgets
import ipywidgets as widgets
from IPython.display import display

#Complementos de Python
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib as mpl
from functools import reduce
from matplotlib import dates as mpl_dates
from sklearn.metrics import mean_squared_error, r2_score

#Módulos Sandia PVLIB-Python
import pvlib
from pvlib import solarposition, irradiance, atmosphere, pvsystem
from pvlib.location import Location
from pvlib.pvsystem import PVSystem, retrieve_sam

if __name__ == '__main__':
    print(f'Successfully executed from {__name__}.')