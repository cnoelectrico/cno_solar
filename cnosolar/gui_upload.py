#########################
#      UPLOAD  GUI      #
#########################

#####
import sys  
sys.path.insert(0, './cnosolar')

import __init__
from IPython import get_ipython
get_ipython().run_line_magic('run', "-i './cnosolar/__init__.py'")
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

#####


import json
import traitlets
import ipywidgets as widgets
from tkinter import Tk, filedialog
from IPython.display import display

gui_layout = widgets.Layout(display='flex', flex_flow='row', justify_content='space-between')

header = widgets.HTML('<h4>Configuración Inicial</h4>', layout=widgets.Layout(height='auto'))

# JSON system configuration file
upload_config = widgets.FileUpload(accept='.json', multiple=False)

# CSV historical data series file
## GUI adapted from https://codereview.stackexchange.com/questions/162920/file-selection-button-for-jupyter-notebook
class SelectFilesButton(widgets.Button):
    '''A file widget that leverages tkinter.filedialog'''
    def __init__(self):
        super(SelectFilesButton, self).__init__()

        # Add the selected_files trait
        self.add_traits(files=traitlets.traitlets.Any()) # List()

        # Create the button
        self.description = 'Select File'
        self.icon = 'square-o'
        #self.style.button_color = 'orange'

        # Set on click behavior
        self.on_click(self.select_files)

    @staticmethod
    def select_files(b):
        '''Generate instance of tkinter.filedialog '''
        # Create Tk root
        root = Tk()

        # Hide the main window
        root.withdraw()

        # Raise the root to the top of all windows
        root.call('wm', 'attributes', '.', '-topmost', True)

        # List of selected fileswill be set to b.value
        b.files = filedialog.askopenfilename(filetypes=(('CSV Files', '.csv'),), 
                                             multiple=False,
                                             title='Select CSV Data File')

        b.description = 'File Selected'
        b.icon = 'check-square-o'
        #b.style.button_color = 'lightgreen'

upload_data = SelectFilesButton()

#################
header2 = widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))

btn = widgets.Button(value=False,
                     description='Cargar Archivos',
                     disabled=False,
                     button_style='', # 'success', 'info', 'warning', 'danger' or ''
                     tooltip='Cargar los archivos JSON y CSV',
                     icon='',
                     layout=widgets.Layout(width='100%', height='auto'))

btn.add_traits(files=traitlets.traitlets.Dict())

output = widgets.Output()

def on_button_clicked(obj):
    btn.description = 'Archivos Cargados'
    btn.icon = 'check-circle'
    with output:
        output.clear_output()

        file_route = './data/' + list(upload_config.value.values())[0]['metadata']['name']
        with open(file_route) as f:
            system_config = json.load(f)

        import data
        df = data.tk_load_csv(file_name=upload_data.files, tz=system_config['tz'])

        btn.files = {'system_configuration': system_config, 'df': df}

btn.on_click(on_button_clicked)

#################

widget_init = [widgets.Box([header]),
               widgets.Box([widgets.Label('Configuración Sistema (JSON)'), upload_config], layout=gui_layout),
               widgets.Box([widgets.Label('Serie Histórica de Datos (CSV)'), upload_data], layout=gui_layout),
               widgets.Box([header2]),
               widgets.Box([widgets.Label(''), btn], layout=gui_layout)]

tab_init = widgets.Box(widget_init, 
                       layout=widgets.Layout(display='flex',
                                             flex_flow='column',
                                             border='solid 0px',
                                             align_items='stretch',
                                             width='50%'))

display(tab_init)
'''
def aaa():
    to_return = {'system_config': None, 'df': None}
    if upload_config.data != []:
#         to_return['upload_config'] = list(upload_config.value.values())[0]['metadata']['name']

        file_route = './data/' + list(upload_config.value.values())[0]['metadata']['name']
        with open(file_route) as f:
            to_return['system_config'] = json.load(f)

    if upload_data.description != 'Select File':
#       to_return['df'] = upload_data.files
        import cno_data
        to_return['df'] = cno_data.tk_load_csv(file_name=upload_data.files, tz=to_return['system_config']['tz'])

    return to_return


# To return a DICT from the uploaded JSON file
def get_config():
    file_route = './data/' + list(upload_config.value.values())[0]['metadata']['name']

    with open(file_route) as f:
        system_config = json.load(f)

    return(system_config)

# To return the ROUTE of the uploaded CSV file
def get_data_route():
    return(upload_data.files)

'''

def test_tab():
    system_config = btn.files['system_configuration']
    df = btn.files['df']

    from cnosolar import pipeline
    from cnosolar import cen
    from cnosolar import data
    from cnosolar import energia_firme
    from cnosolar import complements
    from cnosolar import recurso_potencia

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
    cen_btn.add_traits(files=traitlets.traitlets.Dict())

    def on_button_clicked(obj):
        with cen_output:
            cen_output.clear_output()

            bus_pipeline = pipeline.full_pipeline(system_configuration=system_config, 
                                                  data=df, 
                                                  resolution=60, 
                                                  energy_units='Wh')

            cen_per, cen_pmax = cen.get_cen(ac=bus_pipeline['ac'], 
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
            efirme, enficc_t = energia_firme.enficc_creg(df=df_mes, 
                                                         Kinc=0.9688, 
                                                         IHF=0.1, 
                                                         CEN=cen_btn.files['cen_per'],
                                                         a=3.8e-05, 
                                                         b=-0.0024, 
                                                         c=0.05224, 
                                                         d=-0.3121, 
                                                         Kmedt=0.8540)

            # Energía Firme PVlib + CREG
            __, enficc_v2 = energia_firme.efirme_pvlib_prom(energy=cen_btn.files['bus_pipeline']['energy'])

            # Energía Firme: PVlib + Min
            enficc_v3 = energia_firme.efirme_pvlib_min(energy=cen_btn.files['bus_pipeline']['energy'])

            # Energía Firme: PVlib + Percentil
            enficc_v4 = energia_firme.efirme_pvlib_percentile(energy=cen_btn.files['bus_pipeline']['energy'],
                                                              percentile=1)

            enficc_btn.files = {'efirme':efirme, 'enficc_t':enficc_t, 'enficc_v2':enficc_v2, 
                                'enficc_v3':enficc_v3, 'enficc_v4':enficc_v4}


#             print('ENFICC [kWh/día] =', enficc_t)
#             print('ENFI [kWh/día] -- Mín(Energía Mes PVlib / # Días) =', enficc_v2)
#             print('ENFI [kWh/día] -- Mín(Energía Día PVlib) =', enficc_v3)
#             print('ENFI [kWh/día] -- Percentil(Energía Día PVlib) =', enficc_v4)
        
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
            plt.figure(figsize=(hor, ver))
            plt.bar(x, cen_btn.files['bus_pipeline']['energy']['month']['energy'].tail(12*2), color='#1580E4',
                    label='ENFICC CREG 201 = {} kWh/día\
                            \n\nEF PVlib-Prom = {} kWh/día\
                            \n\nEF PVlib-Min = {} kWh/día\
                            \n\nEF PVlib-Perc ({} %) = {} kWh/día'.format(enficc_btn.files['enficc_t'], 
                                                                          enficc_btn.files['enficc_v2'],
                                                                          enficc_btn.files['enficc_v3'],
                                                                          1,
                                                                          enficc_btn.files['enficc_v4']))

            plt.xticks(x, months);

            complements.plot_specs(title='Energía Mensual',
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

            recurso_potencia.get_curve(poa=cen_btn.files['bus_pipeline']['poa']['poa_global'], 
                                       ac=cen_btn.files['bus_pipeline']['ac'], 
                                       ac_units='kW')

    rr_btn.on_click(on_button_clicked)

    # DISPLAY
    rr_dashboard = widgets.VBox([rr_btn, rr_output])

   
    
    # Tab Dashboard
    item_layout = widgets.Layout(margin='0 0 25px 0')

    tab = widgets.Tab([cen_dashboard, enficc_dashboard, rr_dashboard], layout=item_layout)
    tab.set_title(0, 'CEN')
    tab.set_title(1, 'ENFICC')
    tab.set_title(2, 'Recurso-Potencia')
    display(tab)
    