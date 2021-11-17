# Warnings
import warnings
warnings.filterwarnings(action='ignore')

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