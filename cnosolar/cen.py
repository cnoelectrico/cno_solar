from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import numpy as np
from cnosolar import complements

def get_cen(ac, perc, curve=True):
    '''
    Docstrings
    '''
    pac = np.sort(ac)
    pac_max = np.max(ac)
    
    if pac_max >= 1000000:
        decimals = 0
    else:
        decimals = 4

    # Calculate the proportional values of samples
    p = 1. * np.arange(len(ac)) / (len(ac) - 1)

    # CEN
    cen_per = np.round(np.percentile(ac, perc) / 1000000, decimals) # MW
    cen_pmax = np.round(np.max(ac) / 1000000, decimals) # MW

    print(f'Pac Max. = {cen_pmax} MW\nCEN ({perc} %) = {cen_per} MW')

    # Curve plot
    if curve == True:
        plt.plot(pac, p, label=f'Pac Max. = {cen_pmax} MW\nCEN ({perc} %) = {cen_per} MW')

        complements.plot_specs(title='Capacidad Efectiva Neta',
                               ylabel=f'Percentil',
                               xlabel='Potencia AC, $W$',
                               rot=0, 
                               ylim_min=0, ylim_max=None, 
                               xlim_min=None, xlim_max=None, 
                               loc='best')
        plt.legend(loc='lower right', fontsize=10);
        plt.show()
        
    return cen_per, cen_pmax