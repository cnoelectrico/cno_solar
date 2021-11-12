from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')

import numpy as np
import matplotlib.pyplot as plt
from cnosolar import complements

units = {'kW': 1000, 'MW': 1000000}

def get_curve(poa, ac, ac_units):
    #Least Squares Linear Regression
    y_value = ac / units[ac_units]
    x_value = poa

    #Figure
    plt.plot(x_value, y_value, color='black', ls='', marker='.', ms=1, fillstyle='none',
             label=f'Pac Max. [MW] = {np.round(np.max(ac/units[ac_units]), 2)}')

    complements.plot_specs(title=f'Relación Recurso-Potencia',
                           ylabel=f'Potencia AC, $kW$', #${ac_units}$
                           xlabel='Irradiancia POA, $W/m^2$',
                           rot=0, 
                           ylim_min=0, ylim_max=None, 
                           xlim_min=0, xlim_max=None, 
                           loc='best');
    plt.show()