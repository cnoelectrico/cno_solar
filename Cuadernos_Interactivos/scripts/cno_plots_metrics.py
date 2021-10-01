get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sklearn
import scipy

def plot_specs(title, ylabel, xlabel, rot, ylim_min, ylim_max, xlim_min, xlim_max, loc):
    plt.rcParams['axes.axisbelow'] = True;
    
    plt.title(title, fontsize=15);
    plt.ylabel(ylabel, fontsize=13);
    plt.xlabel(xlabel, fontsize=13);
    
    plt.tick_params(direction='out', length=5, width=0.75, grid_alpha=0.3)
    plt.xticks(rotation=rot)
    plt.ylim(ylim_min, ylim_max)
    plt.xlim(xlim_min, xlim_max)
    plt.grid(True)
    plt.legend(loc=loc, fontsize=9.5)
    plt.tight_layout

'''
Statistic Metrics
'''
def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def median_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.median(np.abs((y_true - y_pred) / y_true)) * 100

def mean_bias_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return (np.sum(y_true - y_pred) / np.sum(y_true)) * 100

def metrics(r2, measured, modeled):
    print('R2: ', r2.round(4))

    metrics_df = pd.DataFrame({'measured': measured, 
                               'modeled': modeled})

    y_true = metrics_df.measured
    y_pred = metrics_df.modeled

    rmse = sklearn.metrics.mean_squared_error(y_true=y_true, y_pred=y_pred, squared=False)
    rmse = (rmse / np.max(y_true)) * 100
    print('RMSE: ', np.round(rmse, 2))

    '''
    MAPE requires to filter the data when y_true=0 --> (y_true - y_pred)/y_true
    '''
    metrics_df = metrics_df.loc[(metrics_df.index.hour >= 7) & (metrics_df.index.hour <= 17) & (metrics_df.measured != 0)]

    y_true = metrics_df.measured
    y_pred = metrics_df.modeled

    mape = median_absolute_percentage_error(y_true=y_true, y_pred=y_pred)
    print('MAPE: ', np.round(mape, 2))
    
def corr_plot(measured_data, modeled_data, title, units):
    data = pd.DataFrame({'measured': measured_data, 
                         'modeled': modeled_data})

    data = data.dropna()

    # Least Squares Linear Regression
    x_value = data.measured
    y_value = data.modeled

    coef = np.polyfit(x_value, y_value, 1)
    poly1d_fn = np.poly1d(coef)

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x_value, y_value)

    # Figure
    axis_lim = int(np.ceil(data.max().max()))

    x = np.linspace(0, axis_lim, axis_lim)
    y_reg = slope*x + intercept
    
    plt.figure()
    ## Correlation Plot
    plt.plot(x_value, poly1d_fn(x_value), '--k',
             label=('Mod = ' + f'{slope.round(2)} $· \:$ Mea $+ \:$' + f'{intercept.round(2)} \n $R^2 = $' + f'{r_value.round(4)}'), 
             color='#1580E4', linewidth=1.5, zorder=10)

    ## Scatter Plot
    plt.plot(x_value, y_value, color='black', ls='', marker='.', ms=0.5, fillstyle='none')

    ## Ideal Correlation-line Plot
    y = x
    plt.plot(x, y, '--', color='#222020', linewidth=0.5)

    plot_specs(title=f'{title}',
              ylabel=f'Modelado, {units}',
              xlabel=f'Medido, {units}',
              rot=0, 
              ylim_min=0, ylim_max=axis_lim, 
              xlim_min=0, xlim_max=axis_lim, 
              loc='best')
    
    plt.show()
    
    # Metrics
    metrics(r2=r_value, measured=x_value, modeled=y_value)
    
def energy_plot():
    pass

def behaviour_plot(data, label, title, ylabel, xlabel, rot, ylim_min, ylim_max, xlim_min, xlim_max, loc):
    data.plot(label=label, color='#1580E4')

    plot_specs(title=title,
               ylabel=ylabel,
               xlabel=xlabel,
               rot=rot, 
               ylim_min=ylim_min, ylim_max=ylim_max, 
               xlim_min=xlim_min, xlim_max=xlim_max, 
               loc=loc)