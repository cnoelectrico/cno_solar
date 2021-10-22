#########################
#     PROTOCOLS  GUI    #
#########################

import json
import traitlets
import numpy as np
import pandas as pd
import ipywidgets as widgets
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
from IPython.display import display
get_ipython().run_line_magic('matplotlib', 'inline')

import cnosolar as cno

def execute():
    gui_layout = widgets.Layout(display='flex', flex_flow='row', justify_content='space-between')

    ## GUI adapted from https://codereview.stackexchange.com/questions/162920/file-selection-button-for-jupyter-notebook
    class SelectFilesButton(widgets.Button):
        '''A file widget that leverages tkinter.filedialog'''
        def __init__(self, file_to_open):
            super(SelectFilesButton, self).__init__()

            # Add the selected_files trait
            self.add_traits(files=traitlets.traitlets.Any()) # List()

            # Create the button
            self.description = 'Seleccionar'
            self.icon = 'square-o'
            #self.style.button_color = 'orange'

            # Set on click behavior
            self.on_click(self.select_files)

            self.file_to_open = file_to_open

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
            if b.file_to_open == 'JSON':
                b.files = filedialog.askopenfilename(filetypes=(('JSON Files', '.json'),), 
                                                     multiple=False,
                                                     title='Select JSON Data File')

            elif b.file_to_open == 'CSV':
                b.files = filedialog.askopenfilename(filetypes=(('CSV Files', '.csv'),), 
                                                     multiple=False,
                                                     title='Select CSV Data File')

            b.description = 'Seleccionado'
            b.icon = 'check-square-o'
            #b.style.button_color = 'lightgreen'

    upload_config = SelectFilesButton(file_to_open='JSON')
    upload_data = SelectFilesButton(file_to_open='CSV')

    # BUTTONS
    btn = widgets.Button(value=False,
                         description='Cargar Archivos',
                         disabled=False,
                         button_style='', # 'success', 'info', 'warning', 'danger' or ''
                         tooltip='Cargar los archivos JSON y CSV',
                         icon='upload',
                         layout=widgets.Layout(width='100%', height='auto'))

    btn.add_traits(files=traitlets.traitlets.Dict())

    output = widgets.Output()

    def on_button_clicked(obj):
        btn.description = 'Archivos Cargados'
        btn.icon = 'check'

        with output:
            output.clear_output()
            with open(upload_config.files) as f:
                system_config = json.load(f)

            df = cno.data.load_csv(file_name=upload_data.files, tz=system_config['tz'])

            btn.files = {'system_configuration': system_config, 'df': df}

    btn.on_click(on_button_clicked)

    # TAB
    widget_init = [widgets.Box([widgets.HTML('<h4>Información Inicial</h4>', layout=widgets.Layout(height='auto'))]),
                   widgets.Box([widgets.Label('Configuración Sistema (.JSON)'), upload_config], layout=gui_layout),
                   widgets.Box([widgets.Label('Serie Histórica de Datos (.CSV)'), upload_data], layout=gui_layout),
                   widgets.Box([widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))]),
                   widgets.Box([widgets.Label(''), btn, output], layout=gui_layout)]

    tab_init = widgets.Box(widget_init, 
                           layout=widgets.Layout(display='flex',
                                                 flex_flow='column',
                                                 border='solid 0px',
                                                 align_items='stretch',
                                                 width='50%'))

    #########################
    #        CEN GUI        #
    #########################

    # CEN Button
    w_cen = widgets.Button(value=False,
                           description='Calcular CEN',
                           disabled=False,
                           button_style='', # 'success', 'info', 'warning', 'danger' or ''
                           tooltip='Cálculo de la Capacidad Efectiva Neta',
                           icon='bolt',
                           style={'description_width': 'initial'},
                           layout=widgets.Layout(width='100%', height='auto'))

    w_cen.add_traits(files=traitlets.traitlets.Dict())
    cen_output = widgets.Output()

    # Percentil
    w_percentil = widgets.BoundedFloatText(value=99, 
                                           min=0, 
                                           max=100, 
                                           step=0.1,
                                           description='',
                                           disabled=False,
                                           style={'description_width': 'initial'})

    # Resolution
    w_resolution = widgets.IntText(value=60,
                                     step=5,
                                     description='',
                                     disabled=False,
                                     style={'description_width': 'initial'})

    # Widget
    widget_cen = [widgets.Box([widgets.HTML('<h4>Capacidad Efectiva Neta</h4>', layout=widgets.Layout(height='auto'))]),
                  widgets.Box([widgets.Label('Percentil [%]'), w_percentil], layout=gui_layout),
                  widgets.Box([widgets.Label('Resolución Tiempo [min]'), w_resolution], layout=gui_layout),
                  widgets.Box([widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))]),
                  w_cen, cen_output]

    def on_button_clicked(obj):
        with cen_output:
            cen_output.clear_output()

            bus_pipeline = cno.pipeline.run(system_configuration=btn.files['system_configuration'], 
                                            data=btn.files['df'], 
                                            num_subarrays=btn.files['system_configuration']['num_arrays'], 
                                            resolution=w_resolution.value, 
                                            energy_units='Wh')


            cen_per, cen_pmax = cno.cen.get_cen(ac=bus_pipeline['system']['ac'], 
                                                perc=w_percentil.value, # Percentil CEN
                                                curve=True)

            w_cen.files = {'bus_pipeline':bus_pipeline, 'cen_per':cen_per, 'cen_pmax':cen_pmax}

    w_cen.on_click(on_button_clicked)

    # Tab
    tab_cen = widgets.Box(widget_cen, layout=widgets.Layout(display='flex',
                                                            flex_flow='column',
                                                            border='solid 0px',
                                                            align_items='stretch',
                                                            width='50%'))


    #########################
    #       ENFICC GUI      #
    #########################

    # ENFICC Button
    w_enficc = widgets.Button(value=False,
                              description='Calcular ENFICC',
                              disabled=False,
                              tooltip='Cálculo de la ENFICC',
                              icon='plug',
                              style={'description_width': 'initial'},
                              layout=widgets.Layout(width='50%', height='auto'))

    w_enficc.add_traits(files=traitlets.traitlets.Dict()) # List()
    enficc_output = widgets.Output()

    # Units Dropdown
    w_units = widgets.Dropdown(options=['', 'Wh', 'kWh', 'MWh'], value='Wh', description='', style={'description_width': 'initial'})

    def on_button_clicked(obj):
        with enficc_output:
            enficc_output.clear_output()

            # Prepare Data
            df = btn.files['df']
            df_hora = df[['GHI', 'Temperature']]
            df_hora['GHI'] = df_hora['GHI'] / 1000 # W to kW
            df_hora = df_hora.loc[df_hora.GHI != 0]

            ghi = df_hora.resample('M').apply(lambda x: x.quantile(0.95)).GHI 
            insolation = df_hora['GHI'].resample('M').sum() # kWh/m2 / month
            temp = df_hora['Temperature'].resample('M').mean()

            df_mes = pd.DataFrame({'GHI': ghi, 'Insolation': insolation,'Temperature': temp})

            # ENFICC CREG 201 de 2017
            efirme, enficc_t = cno.energia_firme.enficc_creg(df=df_mes, 
                                                             Kinc=0.9688, 
                                                             IHF=0.1, 
                                                             CEN=w_cen.files['cen_per'],
                                                             a=3.8e-05, 
                                                             b=-0.0024, 
                                                             c=0.05224, 
                                                             d=-0.3121, 
                                                             Kmedt=0.8540)

            # Energía Firme PVlib + CREG
    #         __, enficc_v2 = energia_firme.efirme_pvlib_prom(energy=w_cen.files['bus_pipeline']['system']['energy'])

    #         # Energía Firme: PVlib + Min
    #         enficc_v3 = energia_firme.efirme_pvlib_min(energy=w_cen.files['bus_pipeline']['system']['energy'])

    #         # Energía Firme: PVlib + Percentil
    #         enficc_v4 = energia_firme.efirme_pvlib_percentile(energy=w_cen.files['bus_pipeline']['system']['energy'],
    #                                                           percentile=1)

    #         w_enficc.files = {'efirme':efirme, 'enficc_t':enficc_t, 'enficc_v2':enficc_v2, 
    #                           'enficc_v3':enficc_v3, 'enficc_v4':enficc_v4}

            w_enficc.files = {'efirme':efirme, 'enficc_t':enficc_t}

    #             print('ENFICC [kWh/día] =', enficc_t)
    #             print('ENFI [kWh/día] -- Mín(Energía Mes PVlib / # Días) =', enficc_v2)
    #             print('ENFI [kWh/día] -- Mín(Energía Día PVlib) =', enficc_v3)
    #             print('ENFI [kWh/día] -- Percentil(Energía Día PVlib) =', enficc_v4)

    w_enficc.on_click(on_button_clicked)

    # ENFICC Graph Button
    enficc_graph = widgets.Button(value=False,
                                  description='Graficar ENFICC',
                                  disabled=False,
                                  tooltip='Gráfica de la ENFICC',
                                  icon='bar-chart',
                                  style={'description_width': 'initial'},
                                  layout=widgets.Layout(width='50%', height='auto'))

    g_output = widgets.Output()

    def on_button_clicked(obj):
        with g_output:
            g_output.clear_output()

            energy_units = w_units.value

            #Energy Error Comparison Plot
            months = ['Jan\n2020', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dec']

            x = np.arange(len(months))

            #Bar Plots            
            hor, ver = 13, 5
            plt.figure(figsize=(hor, ver))

    #         plot_label = 'ENFICC CREG 201 = {} kWh/día\
    #                         \n\nEF PVlib-Prom = {} kWh/día\
    #                         \n\nEF PVlib-Min = {} kWh/día\
    #                         \n\nEF PVlib-Perc ({} %) = {} kWh/día'.format(w_enficc.files['enficc_t'], 
    #                                                                       w_enficc.files['enficc_v2'],
    #                                                                       w_enficc.files['enficc_v3'],
    #                                                                       1,
    #                                                                       w_enficc.files['enficc_v4'])

            plot_label = 'ENFICC CREG 201 = {} kWh/día'.format(w_enficc.files['enficc_t'])

            plt.bar(x, w_cen.files['bus_pipeline']['system']['energy']['month'].energy.tail(12*1), color='#1580E4',
                    label=plot_label)

            plt.xticks(x, months);

            cno.complements.plot_specs(title='Energía Mensual',
                                       ylabel=f'Energía, ${energy_units}$',
                                       xlabel='Tiempo',
                                       rot=0, 
                                       ylim_min=0, ylim_max=None, 
                                       xlim_min=None, xlim_max=None, 
                                       loc='best');
            plt.legend(loc='best', fontsize=10);
            plt.show()

    enficc_graph.on_click(on_button_clicked)


    # Widget
    widget_enficc = [widgets.Box([widgets.HTML('<h4>Energía Firme para Cargo por Confiabilidad</h4>', layout=widgets.Layout(height='auto'))]),
                     widgets.Box([widgets.Label('Unidades Energía [%]'), w_units], layout=gui_layout),
                     widgets.Box([widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))]),
                     widgets.HBox([w_enficc, enficc_graph]), 
                     widgets.VBox([enficc_output, g_output])]

    # Tab
    tab_enficc = widgets.Box(widget_enficc, layout=widgets.Layout(display='flex',
                                                                  flex_flow='column',
                                                                  border='solid 0px',
                                                                  align_items='stretch',
                                                                  width='50%'))


    ###############################
    #            GUI              #
    ###############################

    item_layout = widgets.Layout(margin='0 0 25px 0')

    tab = widgets.Tab([tab_init, tab_cen, tab_enficc], layout=item_layout)
    tab.set_title(0, 'Configuración')
    tab.set_title(1, 'CEN')
    tab.set_title(2, 'ENFICC')
    display(tab)