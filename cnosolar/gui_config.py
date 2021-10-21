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

    w_albedo = widgets.FloatText(value=None,
                                 step=0.01,
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
                       widgets.Box([widgets.Label('Altitud'), w_altitude], layout=gui_layout),
                       widgets.Box([widgets.Label('Huso Horario'), w_timezone], layout=gui_layout),
                       widgets.Box([widgets.Label('Superficie'), w_surface], layout=gui_layout),
                       widgets.Box([widgets.Label('Albedo'), w_albedo], layout=gui_layout)]


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
                                        description='Repositorio',
                                        style={'description_width': 'initial'})

    dropdown_manufac = widgets.Dropdown(options='',
                                        value=None,
                                        disabled=True,
                                        description='Fabricante',
                                        style={'description_width': 'initial'})

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
                                       description='Método',
                                       style={'description_width': 'initial'})

    def handle_toggle(change):
        if change['new'] == 'Repositorio':
            inverter_vbox.children = [inverter_btn, dropdown_invrepo, dropdown_manufac]

        elif change['new'] == 'PVsyst':
            inverter_vbox.children = [inverter_btn, w_upload]

        elif change['new'] == 'Manual':
            inverter_vbox.children = [inverter_btn, dropdown_manual]

    def handle_dropdown_manuf(change):
        inverters = pvlib.pvsystem.retrieve_sam(change['new'])

        manufacturers = []
        manufacturers.append('')
        for string in inverters.transpose().index:
            manufacturers.append(string[:string.index('__')])

        manufacturers.append(change['new'])
        dropdown_manufac.options = list(pd.unique(manufacturers))
        dropdown_manufac.disabled = False

        inverter_vbox.children = [inverter_btn, dropdown_invrepo, dropdown_manufac]

    def handle_dropdown_repo(change): 
        inverters = pvlib.pvsystem.retrieve_sam(dropdown_manufac.options[-1])

        matching = [s for s in inverters.transpose().index if change['new'] in s]
        inv_options = list(inverters[matching].transpose().index)
        inv_options.insert(0, '')

        inv_drop = widgets.Dropdown(options=inv_options,
                                    value=None,
                                    description='Inversor',
                                    style={'description_width': 'initial'})

        inverter_vbox.children = [inverter_btn, dropdown_invrepo, dropdown_manufac, inv_drop]

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
                                     widgets.Box([widgets.Label('C0 [1/W]'), w_C0], layout=gui_layout),
                                     widgets.Box([widgets.Label('C1 [1/V]'), w_C1], layout=gui_layout),
                                     widgets.Box([widgets.Label('C2 [1/V]'), w_C2], layout=gui_layout),
                                     widgets.Box([widgets.Label('C3 [1/V]'), w_C3], layout=gui_layout),
                                     widgets.Box([widgets.Label('$P_{AC}$ Consumo Nocturno [W]'), w_Pnt], layout=gui_layout)])

            inverter_vbox.children = [inverter_btn, dropdown_manual, inv_conf]

        else:
            w_pdc0 = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_eta_inv_nom = widgets.BoundedFloatText(value=None, min=0, max=1, step=0.01, description='', style={'description_width': 'initial'})

            inv_conf = widgets.VBox([widgets.Box([widgets.HTML('<h5>Configuración NREL PVWatts</h5>', layout=widgets.Layout(height='auto'))]),
                                     widgets.Box([widgets.Label('$P_{DC}$ Nominal [W]'), w_pdc0], layout=gui_layout),
                                     widgets.Box([widgets.Label('Eficiencia Nominal [ad.]'), w_eta_inv_nom], layout=gui_layout)])

            inverter_vbox.children = [inverter_btn, dropdown_manual, inv_conf]

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
                                        description='Repositorio',
                                        style={'description_width': 'initial'})

    dropdown_modmanu = widgets.Dropdown(options='',
                                        value=None,
                                        disabled=True,
                                        description='Fabricante',
                                        style={'description_width': 'initial'})

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

    def handle_modtoggle(change):
        if change['new'] == 'Repositorio':
            module_vbox.children = [module_btn, dropdown_modrepo]

        elif change['new'] == 'PVsyst':
            module_vbox.children = [module_btn, w_modupload]

        elif change['new'] == 'Manual':  
            w_T_NOCT = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_A_c = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_Length = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_Width = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_N_s = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_I_sc_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_V_oc_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_I_mp_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_V_mp_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_alpha_sc = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_beta_oc = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_a_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_I_L_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_I_o_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_R_s = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_R_sh_ref = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_Adjust = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_gamma_r = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})
            w_PTC = widgets.FloatText(value=None, description='', style={'description_width': 'initial'})

            mod_conf = widgets.VBox([widgets.Box([widgets.HTML('<h5>Configuración Módulo</h5>', layout=widgets.Layout(height='auto'))]),
                                     widgets.Box([widgets.Label('$T_{NOCT}$  [ºC]'), w_T_NOCT], layout=gui_layout),
                                     widgets.Box([widgets.Label('Área [m$^2$]'), w_A_c], layout=gui_layout),
                                     widgets.Box([widgets.Label('Largo [m]'), w_Length], layout=gui_layout),
                                     widgets.Box([widgets.Label('Ancho [m]'), w_Width], layout=gui_layout),
                                     widgets.Box([widgets.Label('Número Céldas'), w_N_s], layout=gui_layout),
                                     widgets.Box([widgets.Label('$I_{SC_{Ref}}$ [A]'), w_I_sc_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('$V_{OC_{Ref}}$ [V]'), w_V_oc_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('$I_{MP_{Ref}}$ [A]'), w_I_mp_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('$V_{MP_{Ref}}$ [A]'), w_V_mp_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('Coef. Temp. $I_{SC}$ [A/ºC]'), w_alpha_sc], layout=gui_layout),
                                     widgets.Box([widgets.Label('Coef. Temp. $V_{OC}$ [V/ºC]'), w_beta_oc], layout=gui_layout),
                                     widgets.Box([widgets.Label('$n N_s  V_{th}$ [V]'), w_a_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('$I_{L_{Ref}}$ [A]'), w_I_L_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('$I_{L_{O}}$ [A]'), w_I_o_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('$R_s$ [Ohms]'), w_R_s], layout=gui_layout),
                                     widgets.Box([widgets.Label('$R_{sh_{Ref}}$ [Ohms]'), w_R_sh_ref], layout=gui_layout),
                                     widgets.Box([widgets.Label('Adjust [%]'), w_Adjust], layout=gui_layout),
                                     widgets.Box([widgets.Label('Coef. Temp. $P_{MP}$ [1/ºC]'), w_gamma_r], layout=gui_layout),
                                     widgets.Box([widgets.Label('$P_{Max_{PTC}}$ [W]'), w_PTC], layout=gui_layout)])

            module_vbox.children = [module_btn, mod_conf]

    def handle_dropdown_modmanuf(change):
        if change['new'] == 'PVFree':
            dropdown_pvfree = widgets.Dropdown(options=['', 'pvmodule', 'cecmodule'],
                                           value=None,
                                           description='Repositorio',
                                           style={'description_width': 'initial'})

            mod_conf = widgets.VBox([widgets.IntText(value=None, description='ID', style={'description_width': 'initial'})])        

            module_vbox.children = [module_btn, dropdown_modrepo, dropdown_pvfree, mod_conf]

        else:    
            modules = pvlib.pvsystem.retrieve_sam(change['new'])

            manufacturers = []
            manufacturers.append('')
            for string in modules.transpose().index:
                manufacturers.append(string[:string.index('_')])

            manufacturers.append(change['new'])

            dropdown_modmanu.options = list(pd.unique(manufacturers))
            dropdown_modmanu.disabled = False

            module_vbox.children = [module_btn, dropdown_modrepo, dropdown_modmanu]

    def handle_dropdown_modrepo(change):
        modules = pvlib.pvsystem.retrieve_sam(dropdown_modmanu.options[-1])

        matching = [s for s in modules.transpose().index if change['new'] in s]
        mod_options = list(modules[matching].transpose().index)
        mod_options.insert(0, '')

        mod_drop = widgets.Dropdown(options=mod_options,
                                    value=None,
                                    description='Módulo',
                                    style={'description_width': 'initial'})

        module_vbox.children = [module_btn, dropdown_modrepo, dropdown_modmanu, mod_drop]

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

    # OBSERVE
    module_btn.observe(handle_modtoggle, 'value')
    dropdown_modrepo.observe(handle_dropdown_modmanuf, 'value')
    dropdown_modmanu.observe(handle_dropdown_modrepo, 'value')
    modbtn.on_click(on_modbutton_clicked)  

    # TAB
    tab_module = widgets.Box([widgets.HTML("<h4>Método de Configuración</h4>", layout=widgets.Layout(height='auto')), 
                              module_vbox], 
                              layout=widgets.Layout(display='flex',
                                                    flex_flow='column',
                                                    border='solid 0px',
                                                    align_items='stretch',
                                                    width='50%'))

    ###############################
    #  SYSTEM CONFIGURATION TAB   #
    ###############################

    # SUBARRAYS
    w_subarrays = widgets.IntText(value=1, description='', style={'description_width': 'initial'})

    conf_subarrays = widgets.VBox([widgets.Box([widgets.HTML('<h4>Subarrays</h4>', layout=widgets.Layout(height='auto'))]),
                                   widgets.Box([widgets.Label('Cantidad Subarrays'), w_subarrays], layout=gui_layout)])

    # ELECTRICAL CONFIGURATION
    w_mps = widgets.Text(value=None, description='', style={'description_width': 'initial'})
    w_spi = widgets.Text(value=None, description='', style={'description_width': 'initial'})
    w_numinv = widgets.Text(value=None, description='', style={'description_width': 'initial'})
    w_mppt = widgets.Text(value=None, description='', style={'description_width': 'initial'})

    def handle_mppt(change):
        if change['new'] == 1:
            v_mppt = '1'
        else:
            v_mppt = '1, ' * change['new']
            v_mppt = v_mppt[:-2]

        w_mppt.value = v_mppt

    w_subarrays.observe(handle_mppt, 'value')

    conf_elec = widgets.VBox([widgets.Box([widgets.HTML('<h4>Configuración Eléctrica</h4>', layout=widgets.Layout(height='auto'))]),
                              widgets.Box([widgets.Label('Módulos por String'), w_mps], layout=gui_layout),
                              widgets.Box([widgets.Label('Strings por Inversor'), w_spi], layout=gui_layout),
                              widgets.Box([widgets.Label('Número Inversores'), w_numinv], layout=gui_layout),
                              widgets.Box([widgets.Label('Porcentaje MPPT'), w_mppt], layout=gui_layout)])

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

            no_tracker = widgets.VBox([widgets.Box([widgets.Label('Azimutal [º]'), w_Azimuth], layout=gui_layout),
                                       widgets.Box([widgets.Label('Elevación [º]'), w_Tilt], layout=gui_layout)])

            sysconfig_vbox.children = [header_TO, tracker_btn, no_tracker]

        elif change['new'] == 'Seguidor 1-Eje':
            w_AxisTilt = widgets.Text(value=None, description='', style={'description_width': 'initial'})
            w_AxisAzimuth = widgets.Text(value=None, description='', style={'description_width': 'initial'})
            w_MaxAngle = widgets.Text(value=None, description='', style={'description_width': 'initial'})
            w_Racking = widgets.Dropdown(options=['', 'open_rack', 'close_mount', 'insulated_back'], value=None, description='', style={'description_width': 'initial'})
            w_Heigh = widgets.Text(value=None, description='', style={'description_width': 'initial'})

            single_tracker = widgets.VBox([widgets.Box([widgets.Label('Elevación Eje [º]'), w_AxisTilt], layout=gui_layout),
                                           widgets.Box([widgets.Label('Azimutal Eje [º]'), w_AxisAzimuth], layout=gui_layout),
                                           widgets.Box([widgets.Label('Ángulo Máximo [º]'), w_MaxAngle], layout=gui_layout),
                                           widgets.Box([widgets.Label('Racking'), w_Racking], layout=gui_layout),
                                           widgets.Box([widgets.Label('Altura Módulos [m]'), w_Heigh], layout=gui_layout)])

            sysconfig_vbox.children = [header_TO, tracker_btn, single_tracker]

    tracker_btn.observe(handle_toggle, 'value')

    # GLOBAL PARAMETERS
    w_loss = widgets.BoundedFloatText(value=26.9, min=0, max=100, step=0.1, description='', style={'description_width': 'initial'})
    w_dispon = widgets.BoundedFloatText(value=100, min=0, max=100, step=1, description='', style={'description_width': 'initial'})
    w_name = widgets.Text(value='', placeholder='Sufijo extensión .JSON', description='', style={'description_width': 'initial'})

    conf_globalparams = widgets.VBox([widgets.Box([widgets.HTML('<h4>Parámetros Globales</h4>', layout=widgets.Layout(height='auto'))]),
                                      widgets.Box([widgets.Label('Pérdidas [%]'), w_loss], layout=gui_layout),
                                      widgets.Box([widgets.Label('Disponibilidad [%]'), w_dispon], layout=gui_layout),
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
            inverter_name = inverter_vbox.children[3].value
            inverter = dict(pvlib.pvsystem.retrieve_sam(inverters_database)[inverter_name])
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
                modules_name = module_vbox.children[3].value
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
                      'A_c': module_vbox.children[1].children[2].children[1].value,
                      'Length': module_vbox.children[1].children[3].children[1].value,
                      'Width': module_vbox.children[1].children[4].children[1].value,
                      'N_s': module_vbox.children[1].children[5].children[1].value,
                      'I_sc_ref': module_vbox.children[1].children[6].children[1].value,
                      'V_oc_ref': module_vbox.children[1].children[7].children[1].value,
                      'I_mp_ref': module_vbox.children[1].children[8].children[1].value,
                      'V_mp_ref': module_vbox.children[1].children[9].children[1].value,
                      'alpha_sc': module_vbox.children[1].children[10].children[1].value,
                      'beta_oc': module_vbox.children[1].children[11].children[1].value,
                      'a_ref': module_vbox.children[1].children[12].children[1].value,
                      'I_L_ref': module_vbox.children[1].children[13].children[1].value,
                      'I_o_ref': module_vbox.children[1].children[14].children[1].value,
                      'R_s': module_vbox.children[1].children[15].children[1].value,
                      'R_sh_ref': module_vbox.children[1].children[16].children[1].value,
                      'Adjust': module_vbox.children[1].children[17].children[1].value,
                      'gamma_r': module_vbox.children[1].children[18].children[1].value,
                      'PTC': module_vbox.children[1].children[19].children[1].value}

            modules_database = None
            modules_name = None

        return [modules_database, modules_name, module]

    ## Mount
    def check_mount(num_arrays):
        if tracker_btn.value == 'Sin Seguidor': 
            with_tracker = False
            axis_tilt = None
            axis_azimuth = None
            max_angle = None
            module_type = None
            racking_model = None
            module_height = None

            if num_arrays == 1:
                surface_azimuth = float(sysconfig_vbox.children[2].children[0].children[1].value)
                surface_tilt = float(sysconfig_vbox.children[2].children[1].children[1].value)

            elif num_arrays > 1:
                surface_azimuth = str_to_list(sysconfig_vbox.children[2].children[0].children[1].value)
                surface_tilt = str_to_list(sysconfig_vbox.children[2].children[1].children[1].value)

        elif tracker_btn.value == 'Seguidor 1-Eje':
            with_tracker = True
            surface_azimuth = None
            surface_tilt = None
            racking_model = sysconfig_vbox.children[2].children[3].children[1].value
            module_height = sysconfig_vbox.children[2].children[4].children[1].value

            if num_arrays == 1:
                axis_tilt = float(sysconfig_vbox.children[2].children[0].children[1].value)
                axis_azimuth = float(sysconfig_vbox.children[2].children[1].children[1].value)
                max_angle = float(sysconfig_vbox.children[2].children[2].children[1].value)

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

        return [with_tracker, surface_azimuth, surface_tilt, axis_tilt, axis_azimuth, max_angle, module_type, racking_model, module_height]

    ## Electric Configuration
    def check_econfig(num_arrays):
        if num_arrays == 1:
            modules_per_string = int(w_mps.value) #Modules Per String
            strings_per_inverter = int(w_spi.value) #Strings Per Inverter
            num_inverters = int(w_numinv.value)
            per_mppt = float(w_mppt.value)

        elif num_arrays > 1:
            modules_per_string = str_to_list(w_mps.value) #Modules Per String
            strings_per_inverter = str_to_list(w_spi.value) #Strings Per Inverter
            num_inverters = str_to_list(w_numinv.value)
            per_mppt = str_to_list(w_mppt.value)

        return [modules_per_string, strings_per_inverter, num_inverters, per_mppt]

    ## System Configuration
    def sys_config(inverter_status, module_status, mount_status, econfig_status):
        system_configuration = {# Geographic Info
                                'latitude': w_latitude.value,
                                'longitude': w_longitude.value,
                                'tz': w_timezone.value,
                                'altitude': w_altitude.value,
                                'surface_type': w_surface.value,
                                'surface_albedo': w_albedo.value,

                                # Inverter
                                'inverters_database': inverter_status[0],
                                'inverter_name': inverter_status[1],
                                'inverter': dict(inverter_status[2]),
                                'ac_model': inverter_status[3],

                                # PV Module
                                'modules_database': module_status[0],
                                'module_name': module_status[1],
                                'module': dict(module_status[2]),

                                # Mount
                                'with_tracker': mount_status[0],
                                'surface_azimuth': mount_status[1],
                                'surface_tilt': mount_status[2],
                                'axis_tilt': mount_status[3],
                                'axis_azimuth': mount_status[4],
                                'max_angle': mount_status[5],
                                'module_type': mount_status[6],
                                'racking_model': mount_status[7],
                                'module_height': mount_status[8],

                                # Electric Configuration
                                'num_arrays': w_subarrays.value,
                                'modules_per_string': econfig_status[0],
                                'strings_per_inverter': econfig_status[1],
                                'num_inverter': econfig_status[2],
                                'per_mppt': econfig_status[3],

                                # Global Parameters
                                'loss': w_loss.value,
                                'availability': w_dispon.value,
                                'name': w_name.value}

        return system_configuration

    # GUI - Dashboard
    item_layout = widgets.Layout(margin='0 0 25px 0')

    tab = widgets.Tab([tab_location, tab_inverter, tab_module, tab_sysconfig], 
                      layout=item_layout)

    tab.set_title(0, 'Ubicación')
    tab.set_title(1, 'Inversor')
    tab.set_title(2, 'Módulo')
    tab.set_title(3, 'Diseño Planta')

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
                                  button_style='', # 'success', 'info', 'warning', 'danger' or ''
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

