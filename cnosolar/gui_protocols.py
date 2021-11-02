#########################
#     PROTOCOLS  GUI    #
#########################

import json
import traitlets
import numpy as np
import pandas as pd
import cnosolar as cno
import ipywidgets as widgets
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
from IPython.display import display
get_ipython().run_line_magic('matplotlib', 'inline')

import cnosolar as cno

def execute():
    ###############################
    #      DOCUMENTATION TAB      #
    ###############################
    gui_layout = widgets.Layout(display='flex',
                                flex_flow='row',
                                justify_content='space-between')
    
    doc_cen = widgets.HTML('''
                                <h5>Información Geográfica</h5>
                                <ul>
                                  <li> <b>Latitud:</b> Utilice la notación de grados decimales.</li>
                                  <li> <b>Longitud:</b> Utilice la notación de grados decimales.</li>
                                  <li> <b>Altitud:</b> Altitud desde el nivel del mar en metros (m.s.n.m).</li>
                                  <li> <b>Huso Horario:</b> Con referencia a UTC. Por defecto: América/Bogotá (UTC-5).</li>
                                  <li> <b>Superficie:</b> Tipo de superficie para determinar albedo. <span style='color:red'>Opcional si desconoce el albedo</span>.</li>
                                  <li> <b>Albedo:</b> Utilice un valor porcentual en escala entre 0 y 1.</li>
                                </ul>''', layout=widgets.Layout(height='auto'))

    doc_rp = widgets.HTMLMath('''
                                    <h5>Método de Configuración: Repositorio</h5>
                                    <ul>
                                      <li> <b>Repositorio:</b> Repositorio de inversores dispuestos por PVlib. Archivos CSV disponibles en cno_solar/repositorios.</li>
                                      <li> <b>Fabricantes:</b> Lista de fabricantes del repositorio seleccionado.</li>
                                      <li> <b>Inversores:</b> Lista de equipos disponibles en el repositorio según el fabricante escogido.</li>
                                    </ul>

                                    <h5>Método de Configuración: PVsyst</h5>
                                    <ul>
                                      <li> Seleccione el archivo del inversor generado por PVsyst (extensión .OND) y dé clic en 'Cargar OND'.</li>
                                    </ul>

                                    <h5>Método de Configuración: Manual</h5>
                                    <ul>
                                      <li> <b>SNL PVlib</b> 
                                       <ul class='square'>
                                         <li> <b>$P_{AC}$ Nominal:</b> Potencia AC nominal del inversor en W.</li>
                                         <li> <b>$P_{DC}$ Nominal:</b> Potencia DC nominal del inversor en W.</li>
                                         <li> <b>$V_{DC}$ Nominal:</b> Voltaje DC al que se alcanza la Potencia AC nominal con la entrada de Potencia DC en V.</li>
                                         <li> <b>$P_{DC}$ de Arraque:</b> Potencia DC necesaria para iniciar el proceso de inversión en W.</li>
                                         <li> <b>$C_0$:</b> Parámetro que define la curvatura de la relación entre la Potencia AC y Potencia DC en condición STC en 1/W.</li>
                                         <li> <b>$C_1$:</b> Coeficiente empírico que permite que la Potencia DC Nominal varíe linealmente con la el Voltaje DC en 1/V.</li>
                                         <li> <b>$C_2$:</b> Coeficiente empírico que permite que la Potencia DC de Arranque varíe linealmente con la el Voltaje DC en 1/V.</li>
                                         <li> <b>$C_3$:</b> Coeficiente empírico que permite que $C_0$ varíe linealmente con la el Voltaje DC en 1/V.</li>
                                         <li> <b>$P_{AC}$ Consumo Nocturno:</b> Potencia AC consumida por el inversor durante la noche en W.</li>
                                       </ul>
                                      </li>

                                      <li> <b>NREL PVWatts</b> 
                                       <ul class='square'>
                                         <li> <b>$P_{DC}$ Nominal:</b> Potencia DC nominal del inversor en W.</li>
                                         <li> <b>Eficiencia Nominal:</b> Eficiencia nominal del inversor en magnitud adimensional.</li>
                                       </ul>
                                      </li>
                                    </ul>
                                ''', layout=widgets.Layout(height='auto'))


    ac_documentation = widgets.Accordion(children=[doc_cen, doc_rp])
    ac_documentation.set_title(0, 'Tab CEN')
    ac_documentation.set_title(1, 'Tab Recurso-Potencia')

    tab_doc = widgets.Box([widgets.HTML('<h4>Documentación</h4>', layout=widgets.Layout(height='auto')), 
                           widgets.VBox([widgets.Box([ac_documentation], layout=gui_layout)])], 
                           layout=widgets.Layout(display='flex',
                                                 flex_flow='column',
                                                 border='solid 0px',
                                                 align_items='stretch',
                                                 width='100%'))
    
    ###############################
    #           UPLOAD            #
    ###############################
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
                                                     multiple=True,
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

            system_config = []
            for i in range(len(upload_config.files)):
                with open(upload_config.files[i]) as f:
                    system_config.append(json.load(f))

            df = cno.data.load_csv(file_name=upload_data.files, tz=system_config[0]['tz'])

            btn.files = {'system_configuration': system_config, 'df': df}

    btn.on_click(on_button_clicked)

    ###############################
    #             CEN             #
    ###############################
    # CEN Button
    w_cen = widgets.Button(value=False,
                           description='Calcular CEN',
                           disabled=False,
                           button_style='',
                           tooltip='Cálculo de la Capacidad Efectiva Neta',
                           icon='bolt',
                           style={'description_width': 'initial'},
                           layout=widgets.Layout(width='50%', height='auto'))

    w_cen.add_traits(files=traitlets.traitlets.Dict())
    cen_output = widgets.Output()

    # Percentil
    w_cenpercentil = widgets.BoundedFloatText(value=99, 
                                              min=0, 
                                              max=100, 
                                              step=0.1,
                                              description='',
                                              disabled=False,
                                              style={'description_width': 'initial'})
    # Plot Color
    w_cencolor = widgets.ColorPicker(concise=False,
                                     description='',
                                     value='#1580E4',
                                     disabled=False)
    # Pac Units
    w_cenunits = widgets.Dropdown(options=['W', 'kW', 'MW'], value='W', description='', style={'description_width': 'initial'})

    # Download Production Button
    download_cen = widgets.Button(value=False,
                                  description='Descargar Producción',
                                  disabled=False,
                                  button_style='',
                                  tooltip='Descarga CSV de la Producción del Sistema',
                                  icon='download',
                                  layout=widgets.Layout(width='50%', height='auto'))

    downloadcen_output = widgets.Output()

    # Plot Download
    w_downloadcenplot = widgets.Dropdown(options=[('Sí', True), ('No', False)], value=False, description='', style={'description_width': 'initial'})

    # Functions
    def on_button_clicked_cen(obj):
        with cen_output:
            cen_output.clear_output()

            bus_pipeline = cno.pipeline.run(system_configuration=btn.files['system_configuration'], 
                                            data=btn.files['df'],
                                            availability=None,
                                            energy_units='Wh')

            if len(btn.files['system_configuration']) > 1:
                ac_for_cen = bus_pipeline['plant']['ac']
            else:
                ac_for_cen = bus_pipeline['plant']['system']['ac']

            cen_per, cen_pmax = cno.cen.get_cen(ac=ac_for_cen, 
                                                perc=w_cenpercentil.value, # Percentil CEN
                                                color=w_cencolor.value,
                                                mag=w_cenunits.value,
                                                dwnld=w_downloadcenplot.value)

            w_cen.files = {'bus_pipeline':bus_pipeline, 'cen_per':cen_per, 'cen_pmax':cen_pmax}

    w_cen.on_click(on_button_clicked_cen)

    def on_downloadcen_clicked(obj):
        with downloadcen_output:
            cols_to_download = ['Zenith, degree', 'Elevation, degree', 'Azimuth, degree', 'Airmass Relative, ad',  'Airmass Absolute, ad', 'Extraterrestrial Radiation, W/m2', 'POA, W/m2', 'Tmod, C', 'Isc, A', 'Voc, V', 'Idc, A', 'Vdc, V', 'Pdc, W', 'Pac, W', 'Daily Energy, Wh', 'Weekly Energy, Wh', 'Monthly Energy, Wh']

            for superkey in w_cen.files['bus_pipeline'].keys():
                if superkey != 'plant':
                    for key in w_cen.files['bus_pipeline'][superkey].keys():
                        cen_to_download = pd.concat([w_cen.files['bus_pipeline'][superkey][key]['solpos'][['zenith', 'elevation', 'azimuth']].round(2), 
                                                     w_cen.files['bus_pipeline'][superkey][key]['airmass'].round(2),
                                                     w_cen.files['bus_pipeline'][superkey][key]['etr_nrel'].round(2),
                                                     w_cen.files['bus_pipeline'][superkey][key]['poa'].round(2),
                                                     w_cen.files['bus_pipeline'][superkey][key]['temp_cell'].round(2),
                                                     w_cen.files['bus_pipeline'][superkey][key]['dc'][['i_sc', 'v_oc', 'i_mp', 'v_mp', 'p_mp']].round(2),
                                                     w_cen.files['bus_pipeline'][superkey][key]['ac'].round(2),
                                                     w_cen.files['bus_pipeline'][superkey][key]['energy']['day'].round(2),
                                                     w_cen.files['bus_pipeline'][superkey][key]['energy']['week'].round(2),
                                                     w_cen.files['bus_pipeline'][superkey][key]['energy']['month'].round(2)], axis=1)

                        cen_to_download.columns = cols_to_download
                        cen_to_download.to_csv(f'./downloads/pipeline_{superkey}_{key}.csv')

                else:
                    cen_to_download = pd.concat([w_cen.files['bus_pipeline'][superkey]['solpos'][['zenith', 'elevation', 'azimuth']].round(2), 
                                                 w_cen.files['bus_pipeline'][superkey]['airmass'].round(2),
                                                 w_cen.files['bus_pipeline'][superkey]['etr_nrel'].round(2),
                                                 w_cen.files['bus_pipeline'][superkey]['poa'].round(2),
                                                 w_cen.files['bus_pipeline'][superkey]['temp_cell'].round(2),
                                                 w_cen.files['bus_pipeline'][superkey]['dc'][['i_sc', 'v_oc', 'i_mp', 'v_mp', 'p_mp']].round(2),
                                                 w_cen.files['bus_pipeline'][superkey]['ac'].round(2),
                                                 w_cen.files['bus_pipeline'][superkey]['energy']['day'].round(2),
                                                 w_cen.files['bus_pipeline'][superkey]['energy']['week'].round(2),
                                                 w_cen.files['bus_pipeline'][superkey]['energy']['month'].round(2)], axis=1)

                    cen_to_download.columns = cols_to_download
                    cen_to_download.to_csv(f'./downloads/pipeline_{superkey}.csv')

            download_cen.description = 'Producción Descargada'
            download_cen.icon = 'check'

    download_cen.on_click(on_downloadcen_clicked)

    ###############################
    #       ENERGÍA MÍNIMA        #
    ###############################
    eunits = {'Wh': 1, 'kWh': 1000, 'MWh': 1000000}

    # energiamin Button
    w_energiamin = widgets.Button(value=False,
                              description='Calcular Energía Mínima Diaria',
                              disabled=False,
                              tooltip='Cálculo de la Energía Mínima Diaria',
                              icon='plug',
                              style={'description_width': 'initial'},
                              layout=widgets.Layout(width='50%', height='auto'))

    w_energiamin.add_traits(files=traitlets.traitlets.Dict()) # List()
    emin_output = widgets.Output()

    # Percentil
    w_eminpercentil = widgets.BoundedFloatText(value=1, 
                                               min=0, 
                                               max=100, 
                                               step=0.1,
                                               description='',
                                               disabled=False,
                                               style={'description_width': 'initial'})
    # Plot Color
    w_emincolor = widgets.ColorPicker(concise=False,
                                      description='',
                                      value='#1580E4',
                                      disabled=False)
    # Energy Units
    w_eminunits = widgets.Dropdown(options=['Wh', 'kWh', 'MWh'], value='Wh', description='', style={'description_width': 'initial'})

    # Plot Download
    w_downloademinplot = widgets.Dropdown(options=[('Sí', True), ('No', False)], value=False, description='', style={'description_width': 'initial'})

    # energiamin Graph Button
    energiamin_graph = widgets.Button(value=False,
                                      description='Graficar Energía Diaria',
                                      disabled=False,
                                      tooltip='Gráfica de la Energía Diaria',
                                      icon='area-chart',
                                      style={'description_width': 'initial'},
                                      layout=widgets.Layout(width='50%', height='auto'))

    eminplot_output = widgets.Output()

    # Widget
    w_emin = widgets.VBox([widgets.Box([widgets.HTML('<h4>Energía Mínima Diaria</h4>', layout=widgets.Layout(height='auto'))]),
                           widgets.Box([widgets.Label('Percentil [%]'), w_eminpercentil], layout=gui_layout),
                           widgets.Box([widgets.Label('Gráfica - Color'), w_emincolor], layout=gui_layout),
                           widgets.Box([widgets.Label('Gráfica - Magnitud Energía'), w_eminunits], layout=gui_layout),
                           widgets.Box([widgets.Label('Gráfica - Descargar'), w_downloademinplot], layout=gui_layout),
                           widgets.Box([widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))]),
                           widgets.Box([w_energiamin, energiamin_graph], layout=gui_layout),
                           widgets.Box([emin_output], layout=gui_layout),
                           widgets.Box([eminplot_output], layout=gui_layout)])

    ac_emin = widgets.Accordion(children=[w_emin])
    ac_emin.set_title(0, 'Energía Mínima Diaria')

    ac_energiamin = widgets.Box([ac_emin], layout=widgets.Layout(display='flex',
                                                                 flex_flow='column',
                                                                 border='solid 0px',
                                                                 align_items='stretch',
                                                                 width='100%'))

    # Functions
    def on_emin_clicked(obj):
        with emin_output:
            emin_output.clear_output()

            if len(w_cen.files['bus_pipeline'].keys()) == 1:
                energy_data = w_cen.files['bus_pipeline']['plant']['system']['energy']
            else:
                energy_data = w_cen.files['bus_pipeline']['plant']['energy']

            # Energía Firme: PVlib + Percentil
            e_min = cno.energia_minima.pvlib_percentile(energy=energy_data,
                                                        percentile=w_eminpercentil.value)

            w_energiamin.files = {'energiamin': e_min}

    w_energiamin.on_click(on_emin_clicked)

    def on_eminplot_clicked(obj):
        with eminplot_output:
            eminplot_output.clear_output()

            if len(w_cen.files['bus_pipeline'].keys()) == 1:
                energy_to_plot = w_cen.files['bus_pipeline']['plant']['system']['energy']['day']
            else:
                energy_to_plot = w_cen.files['bus_pipeline']['plant']['energy']['day']

            #Bar Plots            
            hor, ver = 13, 5
            plt.figure(figsize=(hor, ver))

            plot_label = 'Energía Mínima ({}%) = {} kWh/día'.format(w_eminpercentil.value, w_energiamin.files['energiamin'])

            dd = energy_to_plot / eunits[w_eminunits.value]

            plt.plot(dd, label=plot_label, marker='.', ms=6.5, linewidth=0.5, color=w_emincolor.value)

            plt.rcParams['axes.axisbelow'] = True;

            plt.title('Energía Diaria', fontsize=15);
            plt.ylabel(f'Energía, ${w_eminunits.value}$', fontsize=13);
            plt.xlabel('Tiempo', fontsize=13);

            plt.tick_params(direction='out', length=5, width=0.75, grid_alpha=0.3)
            plt.xticks(rotation=0)
            plt.ylim(0, None)
            plt.xlim(None, None)
            plt.grid(True)
            plt.legend(loc='best', fontsize=10)
            plt.tight_layout                     

            if w_downloademinplot.value == True:
                plt.savefig('./downloads/daily_energy.pdf', bbox_inches='tight')

            plt.show()

    energiamin_graph.on_click(on_eminplot_clicked)

    # Tab
    widget_protocols = [widgets.Box([widgets.HTML('<h4>Información Inicial</h4>', layout=widgets.Layout(height='auto'))]),
                        widgets.Box([widgets.Label('Configuración Sistema (.JSON)'), upload_config], layout=gui_layout),
                        widgets.Box([widgets.Label('Serie Histórica de Datos (.CSV)'), upload_data], layout=gui_layout),
                        widgets.Box([widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))]),
                        widgets.Box([btn, output], layout=gui_layout),
                        widgets.Box([widgets.HTML('<h4>Capacidad Efectiva Neta</h4>', layout=widgets.Layout(height='auto'))]),
                        widgets.Box([widgets.Label('Percentil [%]'), w_cenpercentil], layout=gui_layout),
                        widgets.Box([widgets.Label('Gráfica - Color'), w_cencolor], layout=gui_layout),
                        widgets.Box([widgets.Label('Gráfica - Magnitud $P_{AC}$'), w_cenunits], layout=gui_layout),
                        widgets.Box([widgets.Label('Gráfica - Descargar'), w_downloadcenplot], layout=gui_layout),
                        widgets.Box([widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))]),
                        widgets.Box([w_cen, download_cen], layout=gui_layout),
                        widgets.Box([cen_output, downloadcen_output], layout=gui_layout),
                        widgets.Box([widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))]),
                        widgets.Box([ac_energiamin], layout=gui_layout)]

    tab_protocols = widgets.Box(widget_protocols, layout=widgets.Layout(display='flex',
                                                                        flex_flow='column',
                                                                        border='solid 0px',
                                                                        align_items='stretch',
                                                                        width='55%'))

    ###############################
    #       RECURSO-POTENCIA      #
    ###############################
    punits = {'W': 1, 'kW': 1000, 'MW': 1000000}
    eunits = {'Wh': 1, 'kWh': 1000, 'MWh': 1000000}

    ###############################
    #           UPLOAD            #
    ###############################
    gui_layout = widgets.Layout(display='flex', flex_flow='row', justify_content='space-between')

    upload_config_rp = SelectFilesButton(file_to_open='JSON')
    upload_data_rp = SelectFilesButton(file_to_open='CSV')

    # BUTTONS
    btn_rp = widgets.Button(value=False,
                            description='Cargar Archivos',
                            disabled=False,
                            button_style='',
                            tooltip='Cargar los archivos JSON y CSV',
                            icon='upload',
                            layout=widgets.Layout(width='100%', height='auto'))

    btn_rp.add_traits(files=traitlets.traitlets.Dict())
    output_upload = widgets.Output()

    def on_button_clicked_rp(obj):
        btn_rp.description = 'Archivos Cargados'
        btn_rp.icon = 'check'

        with output:
            output_upload.clear_output()

            system_config = []
            for i in range(len(upload_config_rp.files)):
                with open(upload_config_rp.files[i]) as f:
                    system_config.append(json.load(f))

            df = cno.data.load_csv(file_name=upload_data_rp.files, tz=system_config[0]['tz'])

            btn_rp.files = {'system_configuration': system_config, 'df': df}

            if len(upload_config_rp.files) == 1:
                v_avail = '1'
            else:
                v_avail = '1, ' * len(upload_config_rp.files)
                v_avail = v_avail[:-2]

            w_availability.value = v_avail

            if len(upload_config_rp.files) == 1:
                sdate = btn_rp.files['df'].index[0]
                edate = btn_rp.files['df'].index[-1]

            else:
                sdate = btn_rp.files['df'].index[0]
                edate = btn_rp.files['df'].index[-1]

            w_startdate.value = sdate
            w_enddate.value = edate

    btn_rp.on_click(on_button_clicked_rp)

    ###############################
    #             R-P             #
    ###############################
    # R-P Button
    w_rp = widgets.Button(value=False,
                          description='Ejecutar',
                          disabled=False,
                          button_style='',
                          tooltip='Cálculo de la Producción según Recurso',
                          icon='fire',
                          style={'description_width': 'initial'},
                          layout=widgets.Layout(width='33%', height='auto'))

    w_rp.add_traits(files=traitlets.traitlets.Dict())
    rp_output = widgets.Output()

    # Graph Button
    plot_btn = widgets.Button(value=False,
                              description='Graficar',
                              disabled=False,
                              tooltip='Gráfica de la Producción',
                              icon='area-chart',
                              style={'description_width': 'initial'},
                              layout=widgets.Layout(width='33%', height='auto'))

    plot_output = widgets.Output()

    # Download Button
    download_rp = widgets.Button(value=False,
                                 description='Descargar',
                                 disabled=False,
                                 button_style='',
                                 tooltip='Descarga CSV de la Producción del Sistema',
                                 icon='download',
                                 layout=widgets.Layout(width='33%', height='auto'))

    downloadrp_output = widgets.Output()

    # Availability
    w_availability = widgets.Text(value=None, description='', style={'description_width': 'initial'})

    # Plot Color
    w_plotcolor = widgets.ColorPicker(concise=False, description='', value='#1580E4', style={'description_width': 'initial'})

    # Relation to Plot
    w_relation = widgets.Dropdown(options=['',
                                           'Tiempo - Potencia DC',
                                           'Tiempo - Potencia AC',
                                           'Tiempo - Energía Diaria',
                                           'Tiempo - Energía Semanal',
                                           'Tiempo - Energía Mensual',
                                           'Irradiancia - Potencia DC',
                                           'Irradiancia - Potencia AC'], 
                                  value='', description='', style={'description_width': 'initial'})

    # Plot Download
    w_downloadplot = widgets.Dropdown(options=[('Sí', True), ('No', False)], value=False, description='', style={'description_width': 'initial'})

    # Power/Energy Units
    w_units = widgets.Dropdown(options=[''], value='', description='', style={'description_width': 'initial'})

    # Dates
    w_startdate = widgets.DatePicker(description='')

    w_enddate = widgets.DatePicker(description='')

    # Functions
    def handle_units(change):
        if change['new'] in ['Tiempo - Potencia DC', 'Tiempo - Potencia AC', 'Irradiancia - Potencia DC', 'Irradiancia - Potencia AC']:
            units_opt = ['W', 'kW', 'MW']
            units_init = 'W'

        elif change['new'] in ['Tiempo - Energía Diaria', 'Tiempo - Energía Semanal', 'Tiempo - Energía Mensual']:
            units_opt = ['Wh', 'kWh', 'MWh']
            units_init = 'Wh'

        else:
            units_opt = ['']
            units_init = ''

        w_units.options = units_opt
        w_units.value = units_init

    w_relation.observe(handle_units, 'value')

    def str_to_list(string):
        l = []
        l.append('[')
        l.append(string) # l.append(string.value)
        l.append(']')
        return json.loads(''.join(l))

    def on_button_clicked_bus(obj):
        with rp_output:
            rp_output.clear_output()

            bus_pipeline = cno.pipeline.run(system_configuration=btn_rp.files['system_configuration'], 
                                            data=btn_rp.files['df'],
                                            availability=str_to_list(w_availability.value),
                                            energy_units='Wh')

            w_rp.files = {'bus_pipeline':bus_pipeline}
            w_rp.description = 'Ejecutado'
            w_rp.icon = 'check'

    w_rp.on_click(on_button_clicked_bus)

    def on_downloadrp_clicked(obj):
        with downloadrp_output:
            cols_to_download = ['Zenith, degree', 'Elevation, degree', 'Azimuth, degree', 'Airmass Relative, ad',  'Airmass Absolute, ad', 'Extraterrestrial Radiation, W/m2', 'POA, W/m2', 'Tmod, C', 'Isc, A', 'Voc, V', 'Idc, A', 'Vdc, V', 'Pdc, W', 'Pac, W', 'Daily Energy, Wh', 'Weekly Energy, Wh', 'Monthly Energy, Wh']

            for superkey in w_rp.files['bus_pipeline'].keys():
                if superkey != 'plant':
                    for key in w_rp.files['bus_pipeline'][superkey].keys():
                        rp_to_download = pd.concat([w_rp.files['bus_pipeline'][superkey][key]['solpos'][['zenith', 'elevation', 'azimuth']].round(2), 
                                                    w_rp.files['bus_pipeline'][superkey][key]['airmass'].round(2),
                                                    w_rp.files['bus_pipeline'][superkey][key]['etr_nrel'].round(2),
                                                    w_rp.files['bus_pipeline'][superkey][key]['poa'].round(2),
                                                    w_rp.files['bus_pipeline'][superkey][key]['temp_cell'].round(2),
                                                    w_rp.files['bus_pipeline'][superkey][key]['dc'][['i_sc', 'v_oc', 'i_mp', 'v_mp', 'p_mp']].round(2),
                                                    w_rp.files['bus_pipeline'][superkey][key]['ac'].round(2),
                                                    w_rp.files['bus_pipeline'][superkey][key]['energy']['day'].round(2),
                                                    w_rp.files['bus_pipeline'][superkey][key]['energy']['week'].round(2),
                                                    w_rp.files['bus_pipeline'][superkey][key]['energy']['month'].round(2)], axis=1)

                        rp_to_download.columns = cols_to_download
                        rp_to_download.to_csv(f'./downloads/pipeline_{superkey}_{key}.csv')

                else:
                    rp_to_download = pd.concat([w_rp.files['bus_pipeline'][superkey]['solpos'][['zenith', 'elevation', 'azimuth']].round(2), 
                                                w_rp.files['bus_pipeline'][superkey]['airmass'].round(2),
                                                w_rp.files['bus_pipeline'][superkey]['etr_nrel'].round(2),
                                                w_rp.files['bus_pipeline'][superkey]['poa'].round(2),
                                                w_rp.files['bus_pipeline'][superkey]['temp_cell'].round(2),
                                                w_rp.files['bus_pipeline'][superkey]['dc'][['i_sc', 'v_oc', 'i_mp', 'v_mp', 'p_mp']].round(2),
                                                w_rp.files['bus_pipeline'][superkey]['ac'].round(2),
                                                w_rp.files['bus_pipeline'][superkey]['energy']['day'].round(2),
                                                w_rp.files['bus_pipeline'][superkey]['energy']['week'].round(2),
                                                w_rp.files['bus_pipeline'][superkey]['energy']['month'].round(2)], axis=1)

                    rp_to_download.columns = cols_to_download
                    rp_to_download.to_csv(f'./downloads/recursopotencia_{superkey}.csv')

            download_rp.description = 'Descargado'
            download_rp.icon = 'check'

    download_rp.on_click(on_downloadrp_clicked)

    def on_plot_clicked(obj):
        with plot_output:
            plot_output.clear_output()

            if len(w_rp.files['bus_pipeline'].keys()) == 1:
                df_to_plot = w_rp.files['bus_pipeline']['plant']['system']
            else:
                df_to_plot = w_rp.files['bus_pipeline']['plant']

            if w_relation.value == 'Tiempo - Potencia DC':
                yy = df_to_plot['dc'][w_startdate.value:w_enddate.value] / punits[w_units.value]

                title = 'Comportamiento Potencia DC'
                xlab = 'Tiempo'
                ylab = f'Potencia, ${w_units.value}$'
                down_label = 'dc_power'

                plt.plot(yy, marker='.', ms=6.5, linewidth=0.5, color=w_emincolor.value)

            elif w_relation.value == 'Tiempo - Potencia AC':
                yy = df_to_plot['ac'][w_startdate.value:w_enddate.value] / punits[w_units.value]

                title = 'Comportamiento Potencia AC'
                xlab = 'Tiempo'
                ylab = f'Potencia, ${w_units.value}$'
                down_label = 'ac_power'

                plt.plot(yy, marker='.', ms=6.5, linewidth=0.5, color=w_emincolor.value)

            elif w_relation.value == 'Tiempo - Energía Diaria':
                yy = df_to_plot['energy']['day'][w_startdate.value:w_enddate.value] / eunits[w_units.value]

                title = 'Comportamiento Energía Diaria'
                xlab = 'Tiempo'
                ylab = f'Energía, ${w_units.value}$'
                down_label = 'daily_energy'

                plt.plot(yy, marker='.', ms=6.5, linewidth=0.5, color=w_emincolor.value)

            elif w_relation.value == 'Tiempo - Energía Semanal':
                yy = df_to_plot['energy']['week'][w_startdate.value:w_enddate.value] / eunits[w_units.value]

                title = 'Comportamiento Energía Semanal'
                xlab = 'Tiempo'
                ylab = f'Energía, ${w_units.value}$'
                down_label = 'weekly_energy'

                plt.plot(yy, marker='.', ms=6.5, linewidth=0.5, color=w_emincolor.value)

            elif w_relation.value == 'Tiempo - Energía Mensual':
                yy = df_to_plot['energy']['month'][w_startdate.value:w_enddate.value] / eunits[w_units.value]

                title = 'Comportamiento Energía Mensual'
                xlab = 'Tiempo'
                ylab = f'Energía, ${w_units.value}$'
                down_label = 'monthly_energy'

                plt.plot(yy, marker='.', ms=6.5, linewidth=0.5, color=w_emincolor.value)

            elif w_relation.value == 'Irradiancia - Potencia DC':
                xx = df_to_plot['poa'][w_startdate.value:w_enddate.value].values
                yy = df_to_plot['dc'][w_startdate.value:w_enddate.value] / punits[w_units.value]

                title = 'Relación Irradiancia vs. Potencia DC'
                xlab = 'Irradiancia POA, W/m2'
                ylab = f'Potencia, ${w_units.value}$'
                down_label = 'irradiance_dcpower'

                plt.plot(xx, yy, ls='', marker='.', ms=0.5, fillstyle='none', color=w_plotcolor.value)

            else:
                xx = df_to_plot['poa'][w_startdate.value:w_enddate.value].values
                yy = df_to_plot['ac'][w_startdate.value:w_enddate.value] / punits[w_units.value]

                title = 'Relación Irradiancia vs. Potencia AC'
                xlab = 'Irradiancia POA, W/m2'
                ylab = f'Potencia, ${w_units.value}$'
                down_label = 'irradiance_acpower'

                plt.plot(xx, yy, ls='', marker='.', ms=0.5, fillstyle='none', color=w_plotcolor.value)

            # Plots
            plt.rcParams['axes.axisbelow'] = True;

            plt.title(title, fontsize=15);
            plt.ylabel(ylab, fontsize=13);
            plt.xlabel(xlab, fontsize=13);

            plt.tick_params(direction='out', length=5, width=0.75, grid_alpha=0.3)
            plt.xticks(rotation=30)
            plt.ylim(0, None)
            plt.xlim(None, None)
            plt.grid(True)
            plt.tight_layout

            if w_downloadplot.value == True:
                plt.savefig(f'./downloads/recursopotencia_{down_label}.pdf', bbox_inches='tight')

            plt.show()

    plot_btn.on_click(on_plot_clicked)

    # Tab
    widget_rp = [widgets.Box([widgets.HTML('<h4>Información Inicial</h4>', layout=widgets.Layout(height='auto'))]),
                 widgets.Box([widgets.Label('Configuración Sistema (.JSON)'), upload_config_rp], layout=gui_layout),
                 widgets.Box([widgets.Label('Serie Histórica de Datos (.CSV)'), upload_data_rp], layout=gui_layout),
                 widgets.Box([widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))]),
                 widgets.Box([btn_rp, output_upload], layout=gui_layout),
                 widgets.Box([widgets.HTML('<h4>Recurso-Potencia</h4>', layout=widgets.Layout(height='auto'))]),
                 widgets.Box([widgets.Label('Disponibilidad [%]'), w_availability], layout=gui_layout),
                 widgets.Box([widgets.HTML('<h5>Gráfica</h5>', layout=widgets.Layout(height='auto'))]),
                 widgets.Box([widgets.Label('Relación'), w_relation], layout=gui_layout),
                 widgets.Box([widgets.Label('Magnitud'), w_units], layout=gui_layout),
                 widgets.Box([widgets.Label('Fecha Inicial'), w_startdate], layout=gui_layout),
                 widgets.Box([widgets.Label('Fecha Final'), w_enddate], layout=gui_layout),
                 widgets.Box([widgets.Label('Color'), w_plotcolor], layout=gui_layout),
                 widgets.Box([widgets.Label('Descargar'), w_downloadplot], layout=gui_layout),
                 widgets.Box([widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))]),
                 widgets.Box([w_rp, plot_btn, download_rp], layout=gui_layout),
                 widgets.Box([rp_output, plot_output, downloadrp_output], layout=gui_layout)]

    tab_rp = widgets.Box(widget_rp, layout=widgets.Layout(display='flex',
                                                          flex_flow='column',
                                                          border='solid 0px',
                                                          align_items='stretch',
                                                          width='55%'))

    ###############################
    #            GUI              #
    ###############################

    item_layout = widgets.Layout(margin='0 0 25px 0')

    tab = widgets.Tab([tab_doc, tab_protocols, tab_rp], layout=item_layout)
    tab.set_title(0, 'Documentación')
    tab.set_title(1, 'CEN')
    tab.set_title(2, 'Recurso-Potencia')
    display(tab)