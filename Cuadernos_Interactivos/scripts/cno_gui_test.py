import sys  
sys.path.insert(0, './scripts')

import traitlets
import pandas as pd
import numpy as np

import ipywidgets as widgets
from IPython.display import display

import cno_libraries
from IPython import get_ipython
get_ipython().run_line_magic('run', "-i './scripts/cno_libraries.py'")
get_ipython().run_line_magic('matplotlib', 'inline')

import matplotlib.pyplot as plt

import cno_pipeline
import cno_cen
import cno_energia_firme
import cno_plots_metrics
import cno_recurso_potencia

# CEN Button
cen_btn = widgets.Button(value=False,
                         description='Calcular CEN',
                         disabled=False,
                         button_style='', # 'success', 'info', 'warning', 'danger' or ''
                         tooltip='Cálculo de la Capacidad Efectiva Neta',
                         icon='bolt',
                         layout=widgets.Layout(width='25%', height='auto'))

cen_output = widgets.Output()

bounded_num = widgets.BoundedFloatText(value=99, 
                                       min=0, 
                                       max=100, 
                                       step=0.1,
                                       description='Percentil',
                                       disabled=False,
                                       layout=widgets.Layout(width='25%', height='auto'))

import traitlets
cen_btn.add_traits(files=traitlets.traitlets.Dict()) # List()

def on_button_clicked(obj):
    with cen_output:
        cen_output.clear_output()

        bus_pipeline = cno_pipeline.full_pipeline(system_configuration=system_config, 
                                                  data=df, 
                                                  resolution=60, 
                                                  energy_units='Wh')

        cen_per, cen_pmax = cno_cen.get_cen(ac=bus_pipeline['ac'], 
                                            perc=bounded_num.value, # Percentil CEN
                                            decimals=4,
                                            curve=True)
        
        cen_btn.files = {'bus_pipeline':bus_pipeline, 'cen_per':cen_per, 'cen_pmax':cen_pmax}

cen_btn.on_click(on_button_clicked)

# DISPLAY
cen_dashboard = widgets.VBox([bounded_num, cen_btn, cen_output])


# ENFICC Button
enficc_btn = widgets.Button(value=False,
                            description='Calcular ENFICC',
                            disabled=False,
                            button_style='', # 'success', 'info', 'warning', 'danger' or ''
                            tooltip='Cálculo de la ENFICC',
                            icon='plug',
                            layout=widgets.Layout(width='25%', height='auto'))

enficc_output = widgets.Output()

import traitlets
enficc_btn.add_traits(files=traitlets.traitlets.Dict()) # List()

def on_button_clicked(obj):
    with enficc_output:
        enficc_output.clear_output()

    # Prepare Data
    df_hora = df[['GHI', 'Temperature']]
    df_hora['GHI'] = df_hora['GHI'] / 1000 # W to kW
    df_hora = df_hora.loc[df_hora.GHI != 0]

    ghi = df_hora.resample('M').apply(lambda x: x.quantile(0.95)).GHI # https://stackoverflow.com/questions/39246664/calculate-percentiles-quantiles-for-a-timeseries-with-resample-or-groupby-pand
    insolation = df_hora['GHI'].resample('M').sum() # kWh/m2 / month
    temp = df_hora['Temperature'].resample('M').mean()

    df_mes = pd.DataFrame({'GHI': ghi, 'Insolation': insolation,'Temperature': temp})

    # ENFICC CREG 201 de 2017
    efirme, enficc_t = cno_energia_firme.enficc_creg(df=df_mes, 
                                                     Kinc=0.9688, 
                                                     IHF=0.1, 
                                                     CEN=cen_btn.files['cen_per'],
                                                     a=3.8e-05, 
                                                     b=-0.0024, 
                                                     c=0.05224, 
                                                     d=-0.3121, 
                                                     Kmedt=0.8540)

    # Energía Firme PVlib + CREG
    __, enficc_v2 = cno_energia_firme.efirme_pvlib_prom(energy=cen_btn.files['bus_pipeline']['energy'])

    # Energía Firme: PVlib + Min
    enficc_v3 = cno_energia_firme.efirme_pvlib_min(energy=cen_btn.files['bus_pipeline']['energy'])

    # Energía Firme: PVlib + Percentil
    enficc_v4 = cno_energia_firme.efirme_pvlib_percentile(energy=cen_btn.files['bus_pipeline']['energy'],
                                                          percentile=1) # ACTUALIZARRR!!!

    enficc_btn.files = {'efirme':efirme, 'enficc_t':enficc_t, 'enficc_v2':enficc_v2, 
                        'enficc_v3':enficc_v3, 'enficc_v4':enficc_v4}
    
enficc_btn.on_click(on_button_clicked)



# ENFICC GRAPH Button
enficc_graph = widgets.Button(value=False,
                            description='Graficar ENFICC',
                            disabled=False,
                            button_style='', # 'success', 'info', 'warning', 'danger' or ''
                            tooltip='Gráfica de la ENFICC',
                            icon='bar-chart',
                            layout=widgets.Layout(width='25%', height='auto'))

g_output = widgets.Output()

def on_button_clicked(obj):
    with g_output:
        g_output.clear_output()

        energy_units = 'Wh' # ACTUALIZARRR!!!

        #Energy Error Comparison Plot
        months = ['Jan\n2019', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dec', 
                  'Jan\n2020', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dec']

        x = np.arange(len(months))

        #Bar Plots
        hor, ver = 13, 5
        plt.figure(figsize=(hor,ver))

        plt.bar(x, cen_btn.files['bus_pipeline']['energy']['month']['energy'].tail(12*2), color='#1580E4',
                label='ENFICC CREG 201 = {} kWh/día\
                        \n\nEF PVlib-CREG = {} kWh/día\
                        \n\nEF PVlib-Min = {} kWh/día\
                        \n\nEF PVlib-Perc ({} %) = {} kWh/día'.format(enficc_btn.files['enficc_t'], 
                                                                      enficc_btn.files['enficc_v2'],
                                                                      enficc_btn.files['enficc_v3'],
                                                                      95,
                                                                      enficc_btn.files['enficc_v4']))

        plt.xticks(x, months);

        cno_plots_metrics.plot_specs(title='Energía Mensual',
                                     ylabel=f'Energía, ${energy_units}$',
                                     xlabel='Tiempo',
                                     rot=0, 
                                     ylim_min=0, ylim_max=None, 
                                     xlim_min=None, xlim_max=None, 
                                     loc='best')
        plt.legend(loc='best', bbox_to_anchor=(1,1), fontsize=9.5);
        plt.show()

enficc_graph.on_click(on_button_clicked)


# DISPLAY
enficc_dashboard = widgets.VBox([widgets.HBox([enficc_btn, enficc_graph]), enficc_output, g_output])

# Rec-Pot Button
rr_btn = widgets.Button(value=False,
                        description='Recurso-Potencia',
                        disabled=False,
                        button_style='', # 'success', 'info', 'warning', 'danger' or ''
                        tooltip='Graficar Recurso-Potencia',
                        icon='line-chart',
                        layout=widgets.Layout(width='25%', height='auto'))

rr_output = widgets.Output()

def on_button_clicked(obj):
    with rr_output:
        rr_output.clear_output()

    cno_recurso_potencia.get_curve(poa=cen_btn.files['bus_pipeline']['poa']['poa_global'], 
                                   ac=cen_btn.files['bus_pipeline']['ac'], 
                                   ac_units='kW')
    
rr_btn.on_click(on_button_clicked)

# DISPLAY
rr_dashboard = widgets.VBox([rr_btn, rr_output])



# Tab Dashboard
item_layout = widgets.Layout(margin='0 0 25px 0')

tab = widgets.Tab([cen_dashboard, enficc_dashboard, rr_dashboard], layout=item_layout)
tab.set_title(0, 'Capacidad Efectiva Neta (CEN)')
tab.set_title(1, 'ENFICC')
tab.set_title(2, 'Recurso-Potencia')
display(tab)

