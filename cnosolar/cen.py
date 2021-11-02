from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import numpy as np

def get_cen(ac, perc, color='#1580E4', mag='W', dwnld=False):
    '''
    Docstrings
    '''
    punits = {'W':1, 'kW': 1000, 'MW': 1000000}
    
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
    plt.plot(pac/punits[mag], p, label=f'Pac Max. = {cen_pmax} MW\nCEN ({perc}%) = {cen_per} MW', linewidth=1.25, color=color)

    plt.rcParams['axes.axisbelow'] = True;

    plt.title('Capacidad Efectiva Neta', fontsize=15);
    plt.ylabel('Percentil', fontsize=13);
    plt.xlabel(f'Potencia AC, ${mag}$', fontsize=13);

    plt.tick_params(direction='out', length=5, width=0.75, grid_alpha=0.3)
    plt.xticks(rotation=0)
    plt.ylim(0, None)
    plt.xlim(None, None)
    plt.grid(True)
    plt.legend(loc='lower right', fontsize=10)
    plt.tight_layout
    
    if dwnld == True:
        plt.savefig('./downloads/cen.pdf', bbox_inches='tight')
        
    plt.show()
    
    return cen_per, cen_pmax