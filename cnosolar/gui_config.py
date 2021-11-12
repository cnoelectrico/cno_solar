###############################
#      CONFIGURATION GUI      #
###############################

import json
import pytz
import pvlib
import requests
import traitlets
import numpy as np
import pandas as pd
import ipywidgets as widgets
from tkinter import Tk, filedialog
from IPython.display import display

from cnosolar.pvsyst_tools import pvsyst

def execute():
    ###############################
    #      DOCUMENTATION TAB      #
    ###############################
    gui_layout = widgets.Layout(display='flex',
                                flex_flow='row',
                                justify_content='space-between')
    
    doc_location = widgets.HTML('''
                                <h5>Información Geográfica</h5>
                                <ul>
                                  <li> <b>Latitud:</b> Utilice la notación de grados decimales.</li>
                                  <li> <b>Longitud:</b> Utilice la notación de grados decimales.</li>
                                  <li> <b>Altitud:</b> Altitud desde el nivel del mar en metros (m.s.n.m).</li>
                                  <li> <b>Humedad Relativa:</b> Humedad relativa en la superficie en valor porcentual.</li>
                                  <li> <b>Presión Atmosférica:</b> Presión atmosférica según la altitud del sitio en Pascales (Pa).</li>
                                  <li> <b>Huso Horario:</b> Con referencia a UTC. Por defecto: América/Bogotá (UTC-5).</li>
                                  <li> <b>Superficie:</b> Tipo de superficie para determinar albedo. <span style='color:red'>Opcional si desconoce el albedo</span>.</li>
                                  <li> <b>Albedo:</b> Utilice un valor porcentual en escala entre 0 y 1.</li>
                                </ul>''', layout=widgets.Layout(height='auto'))
    
    doc_inverter = widgets.HTMLMath('''
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

    doc_module = widgets.HTMLMath('''
                                  <h5>Método de Configuración: Repositorio</h5>
                                  <ul>
                                    <li> <b>Repositorio:</b> Repositorio de módulos fotovoltaicos dispuestos por PVlib (CEC y Sandia). Archivos CSV disponibles en cno_solar/repositorios.</li>
                                    <li> <b>PVFree</b> 
                                     <ul class='square'>
                                       <li> <b>Base de Datos:</b> Repositorio de módulos fotovoltaicos dispuestos en PVFree.</li>
                                       <li> <b>ID:</b> Número de identificación del módulo indicado en PVFree.</li>
                                     </ul>
                                    </li>

                                    <li> <b>CEC y Sandia</b> 
                                     <ul class='square'>
                                       <li> <b>Fabricantes:</b> Lista de fabricantes del repositorio seleccionado.</li>
                                       <li> <b>Módulos:</b> Lista de equipos disponibles en el repositorio según el fabricante escogido.</li>
                                     </ul>
                                    </li>
                                  </ul>

                                  <h5>Método de Configuración: PVsyst</h5>
                                  <ul>
                                    <li> Seleccione el archivo del módulo fotovoltaico generado por PVsyst (extensión .PAN) y dé clic en 'Cargar PAN'.</li>
                                  </ul>

                                  <h5>Método de Configuración: Manual</h5>
                                  <ul>
                                    <li> <b>$T_{NOCT}$:</b> Temperatura nominal de funcionamiento de la celda en ºC. </li>
                                    <li> <b>Tecnología:</b> Tecnología de la celda fotovoltaica. </li>
                                    <li> <b>Número Celdas:</b> Número de celdas fotovoltaicas en serie. </li>
                                    <li> <b>$I_{SC}$ en STC:</b> Corriente de corto circuito en condiciones STC en A. </li>
                                    <li> <b>$V_{OC}$ en STC:</b> Voltaje de circuito abierto en condiciones STC en V. </li>
                                    <li> <b>$I_{MP}$ en STC:</b> Corriente en el punto de máxima potencia en condiciones STC en A. </li>
                                    <li> <b>$V_{MP}$ en STC:</b> Voltaje en el punto de máxima potencia en condiciones STC en V.</b> </li>
                                    <li> <b>Coef. Temp. $I_{SC}$:</b> Coeficiente de temperatura de la corriente de cortocircuito en A/ºC. </li>
                                    <li> <b>Coef. Temp. $V_{OC}$:</b> Coeficiente de temperatura de voltaje de circuito abierto en V/ºC. </li>
                                    <li> <b>Coef. Temp. $P_{MP}$:</b> Coeficiente de temperatura de la potencia en el punto máximo en %/ºC. </li>
                                    <li> <b>$P_{Nominal}$ en STC:</b> Potencia nominal del módulo fotovoltaico en condiciones STC en W.</li>
                                  </ul>
                                  
                                  <h5>Parámetros Bifacialidad</h5>
                                  <ul>
                                    <li> <b>Panel Bifacial:</b> Si el panel fotovoltaico es bifacial o no. </li>
                                    <li> <b>Bifacialidad:</b> Relación entre la eficiencia del lado frontal y posterior del módulo fotovoltaico, medida en condiciones STC. Utilice un valor porcentual en escala entre 0 y 1. </li>
                                    <li> <b>Alto Fila Paneles:</b> Altura de las filas de paneles fotovoltaicos medida en su centro en unidades de metros. </li>
                                    <li> <b>Ancho Fila Paneles:</b> Ancho de las filas de paneles fotovoltaicos en el plano 2D considerado en unidades de metros. </li>
                                  </ul>
                                ''', layout=widgets.Layout(height='auto'))

    doc_sysdesign = widgets.HTML('''
                                 <h5>Subarrays</h5>
                                 <ul>
                                   <li> <b>Cantidad Subarrays:</b> Conjunto de arreglos conectados a un inversor. Cada subarray se compone de módulos en serie por string, strings en paralelo y el número de entradas al inversor (ya sea entradas completas por inversor o número de entradas MPPT).</li>
                                 </ul>

                                 <h5>Configuración Eléctrica</h5>
                                 <ul>
                                   <li> <b>Módulos por String:</b> Cantidad de módulos en serie por string en cada subarray. Para múltiples subarrays, separe los valores con una coma de manera ordenada.</li>
                                   <li> <b>Strings por Inversor:</b> Cantidad de strings en paralelo en cada subarray. Para múltiples subarrays, separe los valores con una coma de manera ordenada.</li>
                                   <li> <b>Porcentaje Entradas:</b> Fracción de potencia manejada por cada entrada (e.g. 1/Número de Entradas o 1/Número MPPT). Para múltiples subarrays, separe los valores con una coma de manera ordenada.</li>
                                   <li> <b>Número de Inversores:</b> Cantidad de inversores con configuración eléctrica exactamente igual a la definida. Permite escalar los cálculos de producción.</li>
                                 </ul>

                                  <h5>Seguidores y Orientación</h5>
                                  <ul>
                                    <li> <b>Sin Seguidor</b> 
                                     <ul class='square'>
                                       <li> <b>Azimutal:</b> Ángulo azimutal en grados decimales (Norte = 0, Sur = 180, Este = 90, Oeste = 270). Para múltiples subarrays, separe los valores con una coma de manera ordenada (también aplica si el azimutal es el mismo).</li>
                                       <li> <b>Elevación:</b> Ángulos de inclinación desde la horizontal en grados decimales. Para múltiples subarrays, separe los valores con una coma de manera ordenada (también aplica si la elevación es la misma).</li>
                                       <li> <b>Racking:</b> Tipo de ventilación del montaje. Se utiliza para identificar un conjunto de parámetros para el modelo de temperatura de la celda.</li>
                                     </ul>
                                    </li>

                                    <li> <b>Seguidor 1-Eje</b><br>
                                    El ángulo de rotación se determina en un sistema de coordenadas diestro. El seguidor define el eje-y positivo, el eje-x positivo está a 90º en sentido horario desde el eje-y y es paralelo a la superficie, y el eje-z positivo es normal a ambos ejes (-x y -y), y está orientado hacia el cielo. El ángulo de rotación es una rotación hacia la derecha alrededor del eje-y en el sistema de coordenadas e indica la posición del seguidor en relación con la horizontal. Por ejemplo, si Azimutal Eje es 180º (orientado al sur) y Elevación Eje es 0º, entonces un ángulo del seguidor de 0º es horizontal, de 30º es una rotación hacia el oeste, y -90º es una rotación al plano vertical hacia el este.

                                     <ul class='square'>
                                       <li> <b>Elevación Eje:</b> Elevación del eje de rotación con respecto a la horizontal en grados decimales. Para múltiples subarrays, separe los valores con una coma de manera ordenada (también aplica si la elevación del eje es la misma).</li>
                                       <li> <b>Azimutal Eje:</b> Ángulo perpendicular al eje de rotación en grados decimales (e.g. un valor de 180º indica una rotación de este a oeste). Para múltiples subarrays, separe los valores con una coma de manera ordenada (también aplica si el azimutal del eje es el mismo).</li>
                                       <li> <b>Ángulo Máximo:</b> Ángulo de rotación máximo del seguidor desde su posición horizontal en grados decimales (e.g. un valor de 90º permite que el seguidor gire hasta una posición vertical en la que el panel mira hacia el horizonte). Para múltiples subarrays, separe los valores con una coma de manera ordenada (también aplica si el ángulo máximo es el mismo).</li>
                                       <li> <b>Racking:</b> Tipo de ventilación del montaje. Se utiliza para identificar un conjunto de parámetros para el modelo de temperatura de la celda.</li>
                                     </ul>
                                    </li>
                                  </ul>

                                 <h5>Parámetros Globales</h5>
                                 <ul>
                                   <li> <b>Pérdidas:</b> Porcentaje de pérdidas globales del sistema. Por defecto: 14.6%.</li>
                                   <li> <b>Nombre Planta:</b> Sufijo al nombre del archivo de configuración (system_config_<i>sufijo</i>). Por defecto: system_config.</li>
                                 </ul>
                                 ''', layout=widgets.Layout(height='auto'))

    ac_documentation = widgets.Accordion(children=[doc_location, doc_inverter, doc_module, doc_sysdesign])
    ac_documentation.set_title(0, 'Tab Ubicación')
    ac_documentation.set_title(1, 'Tab Inversor')
    ac_documentation.set_title(2, 'Tab Módulo')
    ac_documentation.set_title(3, 'Tab Diseño Planta')

    tab_doc = widgets.Box([widgets.HTML('<h4>Documentación</h4>', layout=widgets.Layout(height='auto')), 
                           widgets.VBox([widgets.Box([ac_documentation], layout=gui_layout)])], 
                           layout=widgets.Layout(display='flex',
                                                 flex_flow='column',
                                                 border='solid 0px',
                                                 align_items='stretch',
                                                 width='100%'))
    
    ###############################
    #        LOCATION TAB         #
    ###############################
    surfaces = {'': None,
                'Urbano': 'urban',
                'Césped': 'grass',
                'Césped Fresco': 'fresh grass',
                'Tierra': 'soil',
                'Arena': 'sand',
                'Nieve': 'snow',
                'Nieve Fresca': 'fresh snow',
                'Asfalto': 'asphalt',
                'Hormigón': 'concrete',
                'Aluminio': 'aluminum',
                'Cobre': 'copper',
                'Acero': 'fresh steel',
                'Acero Sucio': 'dirty steel',
                'Mar': 'sea'}

    gui_layout = widgets.Layout(display='flex',
                                flex_flow='row',
                                justify_content='space-between')

    w_latitude = widgets.FloatText(value=0,
                                   step=0.001,
                                   description='',
                                   disabled=False,
                                   style={'description_width': 'initial'})

    w_longitude = widgets.FloatText(value=0,
                                    step=0.01,
                                    description='',
                                    disabled=False,
                                    style={'description_width': 'initial'})

    w_altitude = widgets.FloatText(value=0,
                                   step=1,
                                   description='',
                                   disabled=False,
                                   style={'description_width': 'initial'})

    w_timezone = widgets.Dropdown(options=pytz.all_timezones,
                                  value='America/Bogota',
                                  description='',
                                  style={'description_width': 'initial'})

    w_surface = widgets.Dropdown(options=surfaces,
                                 value=None,
                                 description='',
                                 style={'description_width': 'initial'})

    w_albedo = widgets.BoundedFloatText(value=None,
                                        step=0.01,
                                        min=0,
                                        max=1,
                                        description='',
                                        disabled=False,
                                        style={'description_width': 'initial'})

    w_humidity = widgets.BoundedFloatText(value=0,
                                          min=0,
                                          max=100,
                                          step=1,
                                          description='',
                                          disabled=False,
                                          style={'description_width': 'initial'})
    
    w_pressure = widgets.FloatText(value=101325,
                                   step=1,
                                   description='',
                                   disabled=False,
                                   style={'description_width': 'initial'})
    
    def handle_surface_change(change):
        if change.new != None:
            w_albedo.value = pvlib.irradiance.SURFACE_ALBEDOS[change.new]

    w_surface.observe(handle_surface_change, names='value')

    widget_location = [widgets.Box([widgets.HTML('<h4>Información Geográfica</h4>', layout=widgets.Layout(height='auto'))]),
                       widgets.Box([widgets.Label('Latitud'), w_latitude], layout=gui_layout),
                       widgets.Box([widgets.Label('Longitud'), w_longitude], layout=gui_layout),
                       widgets.Box([widgets.Label('Altitud [m.s.n.m]'), w_altitude], layout=gui_layout),
                       widgets.Box([widgets.Label('Humedad Relativa [%]'), w_humidity], layout=gui_layout),
                       widgets.Box([widgets.Label('Presión Atmosférica  [Pa]'), w_pressure], layout=gui_layout),
                       widgets.Box([widgets.Label('Huso Horario'), w_timezone], layout=gui_layout),
                       widgets.Box([widgets.Label('Superficie'), w_surface], layout=gui_layout),
                       widgets.Box([widgets.Label('Albedo [%]'), w_albedo], layout=gui_layout)]

    tab_location = widgets.Box(widget_location, layout=widgets.Layout(display='flex',
                                                                      flex_flow='column',
                                                                      border='solid 0px',
                                                                      align_items='stretch',
                                                                      width='50%'))

    ###############################
    #        INVERTER TAB         #
    ###############################
    inv_repo = {'': None,
                'CEC': 'CECInverter',
                'Sandia': 'SandiaInverter',
                'Anton Driesse': 'ADRInverter'}

    gui_layout = widgets.Layout(display='flex',
                                flex_flow='row',
                                justify_content='space-between')

    inverter_btn = widgets.ToggleButtons(value=None,
                                         options=['Repositorio', 'PVsyst', 'Manual'],
                                         description='',
                                         disabled=False,
                                         button_style='',
                                         tooltips=['Base de datos de PVlib', 
                                                   'Importar desde PVsyst', 
                                                   'Configuración manual'])

    # REPOSITORY
    # Repository Widgets
    inverter_vbox = widgets.VBox([inverter_btn])

    dropdown_invrepo = widgets.Dropdown(options=inv_repo,
                                        value=None,
                                        description='',
                                        style={'description_width': 'initial'})

    dropdown_manufac = widgets.Dropdown(options='',
                                        value=None,
                                        disabled=True,
                                        description='',
                                        style={'description_width': 'initial'})

    w_dropinvrepo = widgets.VBox([widgets.Box([widgets.Label('Repositorio'), dropdown_invrepo], layout=gui_layout)])
    w_dropmanufac = widgets.VBox([widgets.Box([widgets.Label('Fabricantes'), dropdown_manufac], layout=gui_layout)])
    
    # PVsyst Widgets
    class SelectFilesButton(widgets.Button):
        '''A file widget that leverages tkinter.filedialog'''
        def __init__(self):
            super(SelectFilesButton, self).__init__()

            # Add the selected_files trait
            self.add_traits(files=traitlets.traitlets.Any()) # List()

            # Create the button
            self.description = 'Seleccionar'
            self.icon = 'square-o'
            self.layout = widgets.Layout(width='34%', height='auto')

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
            b.files = filedialog.askopenfilename(filetypes=(('OND Files', '.OND'),), 
                                                 multiple=False,
                                                 title='Select OND Data File')

            b.description = 'Seleccionado'
            b.icon = 'check-square-o'

    upload_btn = SelectFilesButton()

    btn = widgets.Button(value=False,
                         description='Cargar OND',
                         disabled=False,
                         button_style='', # 'success', 'info', 'warning', 'danger' or ''
                         tooltip='Cargar los archivos .OND',
                         icon='circle',
                         layout=widgets.Layout(width='34%', height='auto'))

    btn.add_traits(files=traitlets.traitlets.Dict())

    w_upload = widgets.VBox([widgets.Box([widgets.HTML('<h5> </h5>', layout=widgets.Layout(height='auto'))]), 
                             widgets.Box([widgets.Label('Archivo Inversor (.OND)'), upload_btn, btn], layout=gui_layout)])

    # Manual Widgets
    dropdown_manual = widgets.Dropdown(options=['', 'SNL PVlib', 'NREL PVWatts'],
                                       value=None,
                                       description='')
    
    w_dropmanual = widgets.VBox([widgets.Box([widgets.Label('Formato de Configuración'), dropdown_manual], layout=gui_layout)])

    def handle_toggle(change):
        if change['new'] == 'Repositorio':
            inverter_vbox.children = [inverter_btn, w_dropinvrepo, w_dropmanufac]

        elif change['new'] == 'PVsyst':
            inverter_vbox.children = [inverter_btn, w_upload]

        elif change['new'] == 'Manual':
            inverter_vbox.children = [inverter_btn, w_dropmanual]

    def handle_dropdown_manuf(change):
        inverters = pvlib.pvsystem.retrieve_sam(change['new'])

        manufacturers = []
        manufacturers.append('')
        for string in inverters.transpose().index:
            manufacturers.append(string[:string.index('__')])

        manufacturers.append(change['new'])
        dropdown_manufac.options = list(pd.unique(manufacturers))
        dropdown_manufac.disabled = False

        inverter_vbox.children = [inverter_btn, w_dropinvrepo, w_dropmanufac]

    def handle_dropdown_repo(change): 
        inverters = pvlib.pvsystem.retrieve_sam(dropdown_manufac.options[-1])

        matching = [s for s in inverters.transpose().index if change['new'] in s]
        inv_options = list(inverters[matching].transpose().index)
        inv_options.insert(0, '')

        inv_drop = widgets.Dropdown(options=inv_options,
                                    value=None,
                                    description='',
                                    style={'description_width': 'initial'})
        
        w_dropinv = widgets.VBox([widgets.Box([widgets.Label('Inversores'), inv_drop], layout=gui_layout)])

        inverter_vbox.children = [inverter_btn, w_dropinvrepo, w_dropmanufac, w_dropinv]

    # PVSYST
    def on_button_clicked(obj):
        btn.description = 'OND Cargado'
        btn.icon = 'check-circle'
        with output:
            output.clear_output()
            ond = pvsyst.ond_to_inverter_param(path=upload_btn.files)
            inverter = {'Vac': float(ond['pvGInverter']['TConverter']['VOutConv']), # Voltaje de red (Parámetros principales)
                        'Pso': float(ond['pvGInverter']['TConverter']['PLim1']), # Pthresh
                        'Paco': float(ond['pvGInverter']['TConverter']['PNomConv'])*1000, # Potencia CA máxima
                        'Pdco': float(ond['pvGInverter']['TConverter']['PNomDC'])*1000, # Potencia FV nominal
                        'Pdc0': float(ond['pvGInverter']['TConverter']['PNomDC'])*1000,
                        'Vdco': float(ond['pvGInverter']['TConverter']['VNomEff'].split(',')[1]), # Voltaje medio
                        'Pnt': float(ond['pvGInverter']['Night_Loss']), # Night Loss
                        'Vdcmax': float(ond['pvGInverter']['TConverter']['VAbsMax']), # Alto voltaje -- Voltaje de entrada (Curva de eficiencia)
                        'Idcmax': float(ond['pvGInverter']['TConverter']['IMaxDC']),
                        'Mppt_low': float(ond['pvGInverter']['TConverter']['VMppMin']), # Vmín@Pnom
                        'Mppt_high': float(ond['pvGInverter']['TConverter']['VMPPMax']), # Alto Voltaje
                        'eta_inv_nom': float(ond['pvGInverter']['TConverter']['EfficEuro']),
                        'Name': ond['pvGInverter']['pvCommercial']['Model']}
            btn.files = {'inv': inverter}

    # MANUAL
    def handle_dropdown_manual(change):    
        if change['new'] == 'SNL PVlib':
            w_Paco = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_Pdco = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_Vdco = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_Pso = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_C0 = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_C1 = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_C2 = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_C3 = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_Pnt = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})

            inv_conf = widgets.VBox([widgets.Box([widgets.HTML('<h5>Configuración SNL PVlib</h5>', layout=widgets.Layout(height='auto'))]),
                                     widgets.Box([widgets.Label('$P_{AC}$ Nominal  [W]'), w_Paco], layout=gui_layout),
                                     widgets.Box([widgets.Label('$P_{DC}$ Nominal [W]'), w_Pdco], layout=gui_layout),
                                     widgets.Box([widgets.Label('$V_{DC}$ Nominal [V]'), w_Vdco], layout=gui_layout),
                                     widgets.Box([widgets.Label('$P_{DC}$ de Arraque [W]'), w_Pso], layout=gui_layout),
                                     widgets.Box([widgets.Label('$C_0$ [1/W]'), w_C0], layout=gui_layout),
                                     widgets.Box([widgets.Label('$C_1$ [1/V]'), w_C1], layout=gui_layout),
                                     widgets.Box([widgets.Label('$C_2$ [1/V]'), w_C2], layout=gui_layout),
                                     widgets.Box([widgets.Label('$C_3$ [1/V]'), w_C3], layout=gui_layout),
                                     widgets.Box([widgets.Label('$P_{AC}$ Consumo Nocturno [W]'), w_Pnt], layout=gui_layout)])

            inverter_vbox.children = [inverter_btn, w_dropmanual, inv_conf]

        else:
            w_pdc0 = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_eta_inv_nom = widgets.BoundedFloatText(value=None, min=0, max=1, step=0.01, description='', style={'description_width': 'initial'})

            inv_conf = widgets.VBox([widgets.Box([widgets.HTML('<h5>Configuración NREL PVWatts</h5>', layout=widgets.Layout(height='auto'))]),
                                     widgets.Box([widgets.Label('$P_{DC}$ Nominal [W]'), w_pdc0], layout=gui_layout),
                                     widgets.Box([widgets.Label('Eficiencia Nominal [ad.]'), w_eta_inv_nom], layout=gui_layout)])

            inverter_vbox.children = [inverter_btn, w_dropmanual, inv_conf]

    # OBSERVE
    inverter_btn.observe(handle_toggle, 'value')
    dropdown_invrepo.observe(handle_dropdown_manuf, 'value')
    dropdown_manufac.observe(handle_dropdown_repo, 'value')
    btn.on_click(on_button_clicked)
    dropdown_manual.observe(handle_dropdown_manual, 'value')

    # TAB
    tab_inverter = widgets.Box([widgets.HTML("<h4>Método de Configuración</h4>", layout=widgets.Layout(height='auto')), 
                                inverter_vbox], 
                                layout=widgets.Layout(display='flex',
                                                      flex_flow='column',
                                                      border='solid 0px',
                                                      align_items='stretch',
                                                      width='50%'))

    ###############################
    #         MODULE TAB          #
    ###############################
    mod_repo = {'': None,
                'PVFree': 'PVFree',
                'CEC': 'CECMod',
                'Sandia': 'SandiaMod'}

    gui_layout = widgets.Layout(display='flex',
                                flex_flow='row',
                                justify_content='space-between')

    module_btn = widgets.ToggleButtons(value=None,
                                       options=['Repositorio', 'PVsyst', 'Manual'],
                                       description='',
                                       disabled=False,
                                       button_style='', # 'success', 'info', 'warning', 'danger' or ''
                                       tooltips=['Base de datos de PVlib', 
                                                 'Importar desde PVsyst', 
                                                 'Configuración manual'])

    # REPOSITORY
    # Repository Widgets
    module_vbox = widgets.VBox([module_btn])

    dropdown_modrepo = widgets.Dropdown(options=mod_repo,
                                        value=None,
                                        description='',
                                        style={'description_width': 'initial'})

    dropdown_modmanu = widgets.Dropdown(options='',
                                        value=None,
                                        disabled=True,
                                        description='',
                                        style={'description_width': 'initial'})

    w_dropmodrepo = widgets.VBox([widgets.Box([widgets.Label('Repositorio'), dropdown_modrepo], layout=gui_layout)])
    w_dropmodmanu = widgets.VBox([widgets.Box([widgets.Label('Fabricantes'), dropdown_modmanu], layout=gui_layout)])
    
    # PVsyst Widgets
    class SelectPANButton(widgets.Button):
        '''A file widget that leverages tkinter.filedialog'''
        def __init__(self):
            super(SelectPANButton, self).__init__()

            # Add the selected_files trait
            self.add_traits(files=traitlets.traitlets.Any()) # List()

            # Create the button
            self.description = 'Seleccionar'
            self.icon = 'square-o'
            self.layout = widgets.Layout(width='34%', height='auto')

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
            b.files = filedialog.askopenfilename(filetypes=(('PAN Files', '.PAN'),), 
                                                 multiple=False,
                                                 title='Select PAN Data File')

            b.description = 'Seleccionado'
            b.icon = 'check-square-o'

    upload_modbtn = SelectPANButton()

    modbtn = widgets.Button(value=False,
                            description='Cargar PAN',
                            disabled=False,
                            button_style='', # 'success', 'info', 'warning', 'danger' or ''
                            tooltip='Cargar los archivos .PAN',
                            icon='circle',
                            layout=widgets.Layout(width='34%', height='auto'))

    modbtn.add_traits(files=traitlets.traitlets.Dict())
    modbtn_output = widgets.Output()

    w_modupload = widgets.VBox([widgets.Box([widgets.HTML('<h5> </h5>', layout=widgets.Layout(height='auto'))]), 
                                widgets.Box([widgets.Label('Archivo Módulo (.PAN)'), upload_modbtn, modbtn], layout=gui_layout)])

    # Manual Widgets
    dropdown_modmanual = widgets.Dropdown(options=['', 'SNL PVlib', 'NREL PVWatts'],
                                          value=None,
                                          description='Método',
                                          style={'description_width': 'initial'})

    # BIFACIAL PARAMETERS
    dropdown_bifacial = widgets.Dropdown(options=[('Sí', True), ('No', False)],
                                          value=False,
                                          description='',
                                          style={'description_width': 'initial'})

    w_dropbrifacial = widgets.VBox([widgets.Box([widgets.Label('Panel Bifacial'), dropdown_bifacial], layout=gui_layout)])
    bifacial_vbox = widgets.VBox([w_dropbrifacial])
    
    def handle_modtoggle(change):
        if change['new'] == 'Repositorio':
            module_vbox.children = [module_btn, w_dropmodrepo]

        elif change['new'] == 'PVsyst':
            module_vbox.children = [module_btn, w_modupload]

        elif change['new'] == 'Manual':  
            w_T_NOCT = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_Type = widgets.Dropdown(options=[('Mono-Si', 'monoSi'), ('Multi-Si', 'multiSi'), ('Poli-Si', 'polySi'), ('CIS', 'cis'), ('CIGS', 'cigs'), ('CdTe', 'cdte'), ('Amorfo', 'amorphous')], value=None, description='', style={'description_width': 'initial'})
            w_N_s = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_I_sc_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_V_oc_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_I_mp_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_V_mp_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_alpha_sc = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_beta_oc = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_gamma_r = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_STC = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})

            mod_conf = widgets.VBox([widgets.Box([widgets.HTML('<h5>Configuración Módulo</h5>', layout=widgets.Layout(height='auto'))]),
                                     widgets.Box([widgets.Label('$T_{NOCT}$  [ºC]'), w_T_NOCT], layout=gui_layout),
                                     widgets.Box([widgets.Label('Tecnología'), w_Type], layout=gui_layout),
                                     widgets.Box([widgets.Label('Número Celdas'), w_N_s], layout=gui_layout),
                                     widgets.Box([widgets.Label('$I_{SC}$ en STC [A]'), w_I_sc_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('$V_{OC}$ en STC [V]'), w_V_oc_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('$I_{MP}$ en STC [A]'), w_I_mp_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('$V_{MP}$ en STC [A]'), w_V_mp_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('Coef. Temp. $I_{SC}$ [A/ºC]'), w_alpha_sc], layout=gui_layout),
                                     widgets.Box([widgets.Label('Coef. Temp. $V_{OC}$ [V/ºC]'), w_beta_oc], layout=gui_layout),
                                     widgets.Box([widgets.Label('Coef. Temp. $P_{MP}$ [%/ºC]'), w_gamma_r], layout=gui_layout),
                                     widgets.Box([widgets.Label('$P_{Nominal}$ en STC [W]'), w_STC], layout=gui_layout)])

            module_vbox.children = [module_btn, mod_conf]

    def handle_dropdown_modmanuf(change):
        if change['new'] == 'PVFree':
            dropdown_pvfree = widgets.Dropdown(options=['', 'pvmodule', 'cecmodule'],
                                           value=None,
                                           description='',
                                           style={'description_width': 'initial'})

            pvfree_id = widgets.VBox([widgets.IntText(value=None, description='', style={'description_width': 'initial'})])     

            w_droppvfree = widgets.VBox([widgets.Box([widgets.Label('Base de Datos'), dropdown_pvfree], layout=gui_layout)])
            w_modconf = widgets.VBox([widgets.Box([widgets.Label('ID'), pvfree_id], layout=gui_layout)])
            
            module_vbox.children = [module_btn, w_dropmodrepo, w_droppvfree, w_modconf]

        else:    
            modules = pvlib.pvsystem.retrieve_sam(change['new'])

            manufacturers = []
            manufacturers.append('')
            for string in modules.transpose().index:
                manufacturers.append(string[:string.index('_')])

            manufacturers.append(change['new'])

            dropdown_modmanu.options = list(pd.unique(manufacturers))
            dropdown_modmanu.disabled = False

            module_vbox.children = [module_btn, w_dropmodrepo, w_dropmodmanu]

    def handle_dropdown_modrepo(change):
        modules = pvlib.pvsystem.retrieve_sam(dropdown_modmanu.options[-1])

        matching = [s for s in modules.transpose().index if change['new'] in s]
        mod_options = list(modules[matching].transpose().index)
        mod_options.insert(0, '')

        mod_drop = widgets.Dropdown(options=mod_options,
                                    value=None,
                                    description='',
                                    style={'description_width': 'initial'})

        w_dropmod = widgets.VBox([widgets.Box([widgets.Label('Módulos'), mod_drop], layout=gui_layout)])
        
        module_vbox.children = [module_btn, w_dropmodrepo, w_dropmodmanu, w_dropmod]

    # PVSYST
    def on_modbutton_clicked(obj):
        modbtn.description = 'PAN Cargado'
        modbtn.icon = 'check-circle'

        with modbtn_output:
            modbtn_output.clear_output()
            module = pvsyst.pan_to_module_param(path=upload_modbtn.files)
            module['Adjust'] = 0
            module['IAM'] = module['IAM'].tolist()
            modbtn.files = {'mod': module}
    
    # BIFACIAL 
    def handle_dropdown_bifacial(change):
        if change['new'] == True:
            w_bifaciality = widgets.BoundedFloatText(value=None, min=0, max=1, step=0.1, description='', style={'description_width': 'initial'})
            w_rowheight = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_rowwidth = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})

            bif_conf = widgets.VBox([widgets.Box([widgets.Label('Bifacialidad [%]'), w_bifaciality], layout=gui_layout),
                                     widgets.Box([widgets.Label('Alto Fila Paneles [m]'), w_rowheight], layout=gui_layout),
                                     widgets.Box([widgets.Label('Ancho Fila Paneles [m]'), w_rowwidth], layout=gui_layout)])

            bifacial_vbox.children = [w_dropbrifacial, bif_conf]

        else:
            bifacial_vbox.children = [w_dropbrifacial]
        
    # OBSERVE
    module_btn.observe(handle_modtoggle, 'value')
    dropdown_modrepo.observe(handle_dropdown_modmanuf, 'value')
    dropdown_modmanu.observe(handle_dropdown_modrepo, 'value')
    modbtn.on_click(on_modbutton_clicked)
    dropdown_bifacial.observe(handle_dropdown_bifacial, 'value')

    # TAB
    tab_module = widgets.Box([widgets.HTML('<h4>Método de Configuración</h4>', layout=widgets.Layout(height='auto')), 
                              module_vbox,
                              widgets.HTML('<h4>Parámetros Bifacialidad</h4>', layout=widgets.Layout(height='auto')),
                              bifacial_vbox], 
                              layout=widgets.Layout(display='flex',
                                                    flex_flow='column',
                                                    border='solid 0px',
                                                    align_items='stretch',
                                                    width='50%'))

    ###############################
    #  SYSTEM CONFIGURATION TAB   #
    ###############################

    # SUBARRAYS
    w_subarrays = widgets.IntText(value=0, description='', style={'description_width': 'initial'})

    conf_subarrays = widgets.VBox([widgets.Box([widgets.HTML('<h4>Subarrays</h4>', layout=widgets.Layout(height='auto'))]),
                                   widgets.Box([widgets.Label('Cantidad Subarrays'), w_subarrays], layout=gui_layout)])

    # ELECTRICAL CONFIGURATION
    w_mps = widgets.Text(value=None, description='', style={'description_width': 'initial'})
    w_spi = widgets.Text(value=None, description='', style={'description_width': 'initial'})
    w_mppt = widgets.Text(value=None, description='', style={'description_width': 'initial'})
    w_numinv = widgets.IntText(value=1, description='', style={'description_width': 'initial'})

    def handle_mppt(change):
        if change['new'] == 1:
            v_mppt = '1'
            v_others = '0'
        else:
            v_mppt = '1, ' * change['new']
            v_mppt = v_mppt[:-2]
            v_others = '0, ' * change['new']
            v_others = v_others[:-2]

        w_mppt.value = v_mppt
        w_mps.value = v_others
        w_spi.value = v_others

    w_subarrays.observe(handle_mppt, 'value')

    conf_elec = widgets.VBox([widgets.Box([widgets.HTML('<h4>Configuración Eléctrica</h4>', layout=widgets.Layout(height='auto'))]),
                              widgets.Box([widgets.Label('Módulos por String'), w_mps], layout=gui_layout),
                              widgets.Box([widgets.Label('Strings por Inversor'), w_spi], layout=gui_layout),
                              widgets.Box([widgets.Label('Porcentaje Entradas'), w_mppt], layout=gui_layout),
                              widgets.Box([widgets.Label('Número Inversores'), w_numinv], layout=gui_layout)])

    # TRACKING AND ORIENTATION CONFIGURATION
    header_TO = widgets.HTML("<h4>Seguidores y Orientación</h4>", layout=widgets.Layout(height='auto'))

    tracker_btn = widgets.ToggleButtons(value=None,
                                        options=['Sin Seguidor', 'Seguidor 1-Eje'],
                                        description='',
                                        disabled=False,
                                        button_style='', # 'success', 'info', 'warning', 'danger' or ''
                                        tooltips=['Montaje con estructura fija', 
                                                  'Montaje con single-axis tracker'])

    sysconfig_vbox = widgets.VBox([header_TO, tracker_btn])

    def handle_toggle(change):
        if change['new'] == 'Sin Seguidor':
            w_Azimuth = widgets.Text(value=None, description='', style={'description_width': 'initial'})
            w_Tilt = widgets.Text(value=None, description='', style={'description_width': 'initial'})
            w_Racking = widgets.Dropdown(options=['', 'open_rack', 'close_mount', 'insulated_back'], value=None, description='', style={'description_width': 'initial'})

            if w_subarrays.value == 1:
                v_angles = '0'
            else:
                v_angles = '0, ' * w_subarrays.value
                v_angles = v_angles[:-2]

            w_Azimuth.value = v_angles
            w_Tilt.value = v_angles
            
            no_tracker = widgets.VBox([widgets.Box([widgets.Label('Elevación [º]'), w_Tilt], layout=gui_layout),
                                       widgets.Box([widgets.Label('Azimutal [º]'), w_Azimuth], layout=gui_layout),
                                       widgets.Box([widgets.Label('Racking'), w_Racking], layout=gui_layout)])

            sysconfig_vbox.children = [header_TO, tracker_btn, no_tracker]

        elif change['new'] == 'Seguidor 1-Eje':
            w_AxisTilt = widgets.Text(value=None, description='', style={'description_width': 'initial'})
            w_AxisAzimuth = widgets.Text(value=None, description='', style={'description_width': 'initial'})
            w_MaxAngle = widgets.Text(value=None, description='', style={'description_width': 'initial'})
            w_Racking = widgets.Dropdown(options=['', 'open_rack', 'close_mount', 'insulated_back'], value=None, description='', style={'description_width': 'initial'})

            if w_subarrays.value == 1:
                v_angles = '0'
            else:
                v_angles = '0, ' * w_subarrays.value
                v_angles = v_angles[:-2]

            w_AxisTilt.value = v_angles
            w_AxisAzimuth.value = v_angles
            w_MaxAngle.value = v_angles
            
            single_tracker = widgets.VBox([widgets.Box([widgets.Label('Elevación Eje [º]'), w_AxisTilt], layout=gui_layout),
                                           widgets.Box([widgets.Label('Azimutal Eje [º]'), w_AxisAzimuth], layout=gui_layout),
                                           widgets.Box([widgets.Label('Ángulo Máximo [º]'), w_MaxAngle], layout=gui_layout),
                                           widgets.Box([widgets.Label('Racking'), w_Racking], layout=gui_layout)])

            sysconfig_vbox.children = [header_TO, tracker_btn, single_tracker]

    tracker_btn.observe(handle_toggle, 'value')

    # GLOBAL PARAMETERS
    w_loss = widgets.BoundedFloatText(value=14.6, min=0, max=100, step=0.1, description='', style={'description_width': 'initial'})
    w_name = widgets.Text(value='', placeholder='Sufijo extensión .JSON', description='', style={'description_width': 'initial'})

    conf_globalparams = widgets.VBox([widgets.Box([widgets.HTML('<h4>Parámetros Globales</h4>', layout=widgets.Layout(height='auto'))]),
                                      widgets.Box([widgets.Label('Pérdidas [%]'), w_loss], layout=gui_layout),
                                      widgets.Box([widgets.Label('Nombre Planta'), w_name], layout=gui_layout)])

    # TAB
    tab_sysconfig = widgets.Box([conf_subarrays,
                                 conf_elec,
                                 sysconfig_vbox,
                                 conf_globalparams], 
                                 layout=widgets.Layout(display='flex',
                                                       flex_flow='column',
                                                       border='solid 0px',
                                                       align_items='stretch',
                                                       width='50%'))

    ###############################
    #            GUI              #
    ###############################

    # Str to List
    def str_to_list(string):
        l = []
        l.append('[')
        l.append(string) # l.append(string.value)
        l.append(']')
        return json.loads(''.join(l))

    # Status Check
    ## Inverter
    def check_inverter():
        if inverter_btn.value == 'Repositorio':
            inverters_database = dropdown_invrepo.value
            inverter_name = inverter_vbox.children[3].children[0].children[1].value
            inverter = dict(pvlib.pvsystem.retrieve_sam(inverters_database)[inverter_name])
            inverter['Vac'] = float(inverter['Vac'])
            ac_model = 'sandia'

        if inverter_btn.value == 'PVsyst':
            inverter = btn.files['inv']

            ac_model = 'pvwatts'
            inverters_database = None
            inverter_name = None

        if inverter_btn.value == 'Manual':
            if dropdown_manual.value == 'SNL PVlib':
                inverter = {'Paco': inverter_vbox.children[2].children[1].children[1].value,
                            'Pdco': inverter_vbox.children[2].children[2].children[1].value,
                            'Vdco': inverter_vbox.children[2].children[3].children[1].value,
                            'Pso': inverter_vbox.children[2].children[4].children[1].value,
                            'C0': inverter_vbox.children[2].children[5].children[1].value,
                            'C1': inverter_vbox.children[2].children[6].children[1].value,
                            'C2': inverter_vbox.children[2].children[7].children[1].value,
                            'C3': inverter_vbox.children[2].children[8].children[1].value,
                            'Pnt': inverter_vbox.children[2].children[9].children[1].value}

                ac_model = 'sandia'

            elif dropdown_manual.value == 'NREL PVWatts':
                inverter = {'pdc0': inverter_vbox.children[2].children[1].children[1].value,
                            'eta_inv_nom': inverter_vbox.children[2].children[2].children[1].value,
                            'eta_inv_ref': 0.9637}

                ac_model = 'pvwatts'

            inverters_database = None
            inverter_name = None

        return [inverters_database, inverter_name, inverter, ac_model]

    ## Module
    def check_module():
        if module_btn.value == 'Repositorio':
            if dropdown_modrepo.value != 'PVFree':
                modules_database = dropdown_modrepo.value
                modules_name = module_vbox.children[3].children[0].children[1].value
                module = dict(pvlib.pvsystem.retrieve_sam(modules_database)[modules_name])

            else:
                modules_database = dropdown_modrepo.value
                module = dict(requests.get(f'https://pvfree.herokuapp.com/api/v1/{module_vbox.children[2].value}/{module_vbox.children[3].children[0].value}/').json())
                modules_name = module['Name']        

        if module_btn.value == 'PVsyst':
            module = modbtn.files['mod']
            module['a_ref'] = module['Gamma'] * module['NCelS'] * (1.38e-23 * (273.15 + 25) / 1.6e-19)

            modules_database = None
            modules_name = None           

        if module_btn.value == 'Manual':
            module = {'T_NOCT': module_vbox.children[1].children[1].children[1].value,
                      'Technology': module_vbox.children[1].children[2].children[1].value,
                      'N_s': module_vbox.children[1].children[3].children[1].value,
                      'I_sc_ref': module_vbox.children[1].children[4].children[1].value,
                      'V_oc_ref': module_vbox.children[1].children[5].children[1].value,
                      'I_mp_ref': module_vbox.children[1].children[6].children[1].value,
                      'V_mp_ref': module_vbox.children[1].children[7].children[1].value,
                      'alpha_sc': module_vbox.children[1].children[8].children[1].value,
                      'beta_oc': module_vbox.children[1].children[9].children[1].value,
                      'gamma_r': module_vbox.children[1].children[10].children[1].value,
                      'STC': module_vbox.children[1].children[11].children[1].value}
            
            I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, Adjust = pvlib.ivtools.sdm.fit_cec_sam(celltype=module['Technology'], 
                                                                                           v_mp=module['V_mp_ref'], 
                                                                                           i_mp=module['I_mp_ref'], 
                                                                                           v_oc=module['V_oc_ref'], 
                                                                                           i_sc=module['I_sc_ref'], 
                                                                                           alpha_sc=module['alpha_sc'], 
                                                                                           beta_voc=module['beta_oc'], 
                                                                                           gamma_pmp=module['gamma_r'], 
                                                                                           cells_in_series=module['N_s'], 
                                                                                           temp_ref=25)

            module.update({'I_L_ref':I_L_ref, 
                           'I_o_ref':I_o_ref,
                           'R_s':R_s, 
                           'R_sh_ref':R_sh_ref, 
                           'a_ref':a_ref,
                           'Adjust':Adjust})

            modules_database = None
            modules_name = None
            
        if bifacial_vbox.children[0].children[0].children[1].value == False:
            bifacial = False
            bifaciality = 0
            row_height = 0
            row_width = 0
        else:
            bifacial = True
            bifaciality = bifacial_vbox.children[1].children[0].children[1].value
            row_height = bifacial_vbox.children[1].children[1].children[1].value
            row_width = bifacial_vbox.children[1].children[2].children[1].value
        
        return [modules_database, modules_name, module, bifacial, bifaciality, row_height, row_width]

    ## Mount
    def check_mount(num_arrays):
        if tracker_btn.value == 'Sin Seguidor': 
            with_tracker = False
            axis_tilt = None
            axis_azimuth = None
            max_angle = None
            racking_model = sysconfig_vbox.children[2].children[2].children[1].value

            if num_arrays == 1:
                surface_tilt = [float(sysconfig_vbox.children[2].children[0].children[1].value)]
                surface_azimuth = [float(sysconfig_vbox.children[2].children[1].children[1].value)]

            elif num_arrays > 1:
                surface_tilt = str_to_list(sysconfig_vbox.children[2].children[0].children[1].value)
                surface_azimuth = str_to_list(sysconfig_vbox.children[2].children[1].children[1].value)
                
            if racking_model == 'open_rack':
                module_type = 'open_rack_glass_glass'

            elif racking_model == 'close_mount':
                module_type = 'close_mount_glass_glass'

            elif racking_model == 'insulated_back':
                module_type = 'insulated_back_glass_polymer'

        elif tracker_btn.value == 'Seguidor 1-Eje':
            with_tracker = True
            surface_azimuth = None
            surface_tilt = None
            racking_model = sysconfig_vbox.children[2].children[3].children[1].value

            if num_arrays == 1:
                axis_tilt = [float(sysconfig_vbox.children[2].children[0].children[1].value)]
                axis_azimuth = [float(sysconfig_vbox.children[2].children[1].children[1].value)]
                max_angle = [float(sysconfig_vbox.children[2].children[2].children[1].value)]

            elif num_arrays > 1:
                axis_tilt = str_to_list(sysconfig_vbox.children[2].children[0].children[1].value)
                axis_azimuth = str_to_list(sysconfig_vbox.children[2].children[1].children[1].value)
                max_angle = str_to_list(sysconfig_vbox.children[2].children[2].children[1].value)           

            if racking_model == 'open_rack':
                module_type = 'open_rack_glass_glass'

            elif racking_model == 'close_mount':
                module_type = 'close_mount_glass_glass'

            elif racking_model == 'insulated_back':
                module_type = 'insulated_back_glass_polymer'

        return [with_tracker, surface_azimuth, surface_tilt, axis_tilt, axis_azimuth, max_angle, module_type, racking_model]

    ## Electric Configuration
    def check_econfig(num_arrays):
        num_inverters = int(w_numinv.value)
        if num_arrays == 1:
            modules_per_string = [int(w_mps.value)] #Modules Per String
            strings_per_inverter = [int(w_spi.value)] #Strings Per Inverter
            per_mppt = [float(w_mppt.value)]

        elif num_arrays > 1:
            modules_per_string = str_to_list(w_mps.value) #Modules Per String
            strings_per_inverter = str_to_list(w_spi.value) #Strings Per Inverter
            per_mppt = str_to_list(w_mppt.value)

        return [modules_per_string, strings_per_inverter, per_mppt, num_inverters]

    ## System Configuration
    def sys_config(inverter_status, module_status, mount_status, econfig_status):
        system_configuration = {# Geographic Info
                                'latitude': w_latitude.value,
                                'longitude': w_longitude.value,
                                'tz': w_timezone.value,
                                'altitude': w_altitude.value,
                                'surface_type': w_surface.value,
                                'surface_albedo': w_albedo.value,
                                'relative_humidity': w_humidity.value,
                                'pressure': w_pressure.value,

                                # Inverter
                                'inverters_database': inverter_status[0],
                                'inverter_name': inverter_status[1],
                                'inverter': dict(inverter_status[2]),
                                'ac_model': inverter_status[3],

                                # PV Module
                                'modules_database': module_status[0],
                                'module_name': module_status[1],
                                'module': dict(module_status[2]),
                                'bifacial': module_status[3],
                                'bifaciality': module_status[4],
                                'row_height': module_status[5],
                                'row_width': module_status[6],
            
                                # Mount
                                'with_tracker': mount_status[0],
                                'surface_azimuth': mount_status[1],
                                'surface_tilt': mount_status[2],
                                'axis_tilt': mount_status[3],
                                'axis_azimuth': mount_status[4],
                                'max_angle': mount_status[5],
                                'module_type': mount_status[6],
                                'racking_model': mount_status[7],

                                # Electric Configuration
                                'num_arrays': w_subarrays.value,
                                'modules_per_string': econfig_status[0],
                                'strings_per_inverter': econfig_status[1],
                                'per_mppt': econfig_status[2],
                                'num_inverter': econfig_status[3],

                                # Global Parameters
                                'loss': w_loss.value,
                                'name': w_name.value}

        return system_configuration

    # GUI - Dashboard
    item_layout = widgets.Layout(margin='0 0 25px 0')

    tab = widgets.Tab([tab_doc, tab_location, tab_inverter, tab_module, tab_sysconfig], 
                      layout=item_layout)
    
    tab.set_title(0, 'Documentación')
    tab.set_title(1, 'Ubicación')
    tab.set_title(2, 'Inversor')
    tab.set_title(3, 'Módulo')
    tab.set_title(4, 'Diseño Planta')

    # Config Button
    genconfig_btn = widgets.Button(value=False,
                                   description='Generar Configuración',
                                   disabled=False,
                                   button_style='', # 'success', 'info', 'warning', 'danger' or ''
                                   tooltip='Generar Configuración del Sistema',
                                   icon='gear',
                                   layout=widgets.Layout(width='25%', height='auto'))

    genconfig_output = widgets.Output()

    def on_genconfig_clicked(obj):    
        with genconfig_output:
            genconfig_output.clear_output()

            inverter_status = check_inverter()
            module_status = check_module()
            mount_status = check_mount(num_arrays=w_subarrays.value)
            econfig_status = check_econfig(num_arrays=w_subarrays.value)

            system_configuration = sys_config(inverter_status, module_status, mount_status, econfig_status)

            genconfig_btn.description = 'Configuración Generada'
            genconfig_btn.icon = 'check'

    genconfig_btn.on_click(on_genconfig_clicked)

    # Download Button
    download_btn = widgets.Button(value=False,
                                  description='Descargar Configuración',
                                  disabled=False,
                                  button_style='',
                                  tooltip='Descarga JSON de la Configuración del Sistema',
                                  icon='download',
                                  layout=widgets.Layout(width='25%', height='auto'))
    output = widgets.Output()

    def on_button_clicked(obj):
        with output:
            output.clear_output()

            inverter_status = check_inverter()
            module_status = check_module()
            mount_status = check_mount(num_arrays=w_subarrays.value)
            econfig_status = check_econfig(num_arrays=w_subarrays.value)
            system_configuration = sys_config(inverter_status, module_status, mount_status, econfig_status)

            if w_name.value != '':
                json_file = f'system_config_{w_name.value}.json'
            else:
                json_file = 'system_config.json'

            with open(json_file, 'w') as f:
                json.dump(system_configuration, f, indent=2)

            download_btn.description = 'Configuración Descargada'
            download_btn.icon = 'check'

    download_btn.on_click(on_button_clicked)

    btns = widgets.HBox([genconfig_btn, download_btn])
    out_btns = widgets.HBox([genconfig_output, output])

    dashboard = widgets.VBox([tab, btns, out_btns])
    display(dashboard)
