###############################
#      CONFIGURATION GUI      #
###############################

import json
import pytz
import pvlib
import requests
import ipywidgets as widgets
from IPython.display import display

# Dicts
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

inv_repo = {'': None,
            'CEC': 'CECInverter',
            'Sandia': 'SandiaInverter',
            'Anton Driesse': 'ADRInverter'}

mod_repo = {'': None,
            'PVFree': 'PVFree',
            'CEC': 'CECMod',
            'Sandia': 'SandiaMod'}

# Location Tab
gui_layout = widgets.Layout(display='flex',
                            flex_flow='row',
                            justify_content='space-between')

header = widgets.HTML("<h4>Información Geográfica</h4>", layout=widgets.Layout(height='auto'))

w_latitude = widgets.FloatText(value=4.604535,
                               step=0.001,
                               description='',
                               disabled=False,
                               style={'description_width': 'initial'})

w_longitude = widgets.FloatText(value=-74.066038,
                                step=0.001,
                                description='',
                                disabled=False,
                                style={'description_width': 'initial'})

w_altitude = widgets.FloatText(value=2632,
                               step=1,
                               description='',
                               disabled=False,
                               style={'description_width': 'initial'})

w_time_zone = widgets.Dropdown(options=pytz.all_timezones,
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

widget_location = [widgets.Box([header]),
                   widgets.Box([widgets.Label('Latitud'), w_latitude], layout=gui_layout),
                   widgets.Box([widgets.Label('Longitud'), w_longitude], layout=gui_layout),
                   widgets.Box([widgets.Label('Altitud'), w_altitude], layout=gui_layout),
                   widgets.Box([widgets.Label('Huso Horario'), w_time_zone], layout=gui_layout),
                   widgets.Box([widgets.Label('Superficie'), w_surface], layout=gui_layout),
                   widgets.Box([widgets.Label('Albedo'), w_albedo], layout=gui_layout)]


tab_location = widgets.Box(widget_location, 
                           layout=widgets.Layout(display='flex',
                                                 flex_flow='column',
                                                 border='solid 0px',
                                                 align_items='stretch',
                                                 width='50%'))

# Inverter Tab
header = widgets.HTML("<h4>Método de Configuración</h4>", layout=widgets.Layout(height='auto'))

inverter_btn = widgets.ToggleButtons(value=None,
                                     options=['Repositorio', 'PVsyst', 'Manual'],
                                     description='',
                                     disabled=False,
                                     button_style='', # 'success', 'info', 'warning', 'danger' or ''
                                     tooltips=['Configuración desde bases de datos en PVlib', 
                                               'Configuración desde bases de datos en PVsyst', 
                                               'Configuración manual'])

inverter_vbox = widgets.VBox([inverter_btn])

dropdown_invrepo = widgets.Dropdown(options=inv_repo,
                                    value=None,
                                    description='Repositorio:',
                                    style={'description_width': 'initial'})

dropdown_pvsyst = widgets.Dropdown(options=['', 'pvmodule', 'cecmodule'],
                                   value=None,
                                   description='Repositorio:',
                                   style={'description_width': 'initial'})

dropdown_manual = widgets.Dropdown(options=['', 'SNL PVlib', 'NREL PVWatts'],
                                   value=None,
                                   description='Método:',
                                   style={'description_width': 'initial'})

def handle_toggle(change):
    if change['new'] == 'Repositorio':
        inverter_vbox.children = [inverter_btn, dropdown_invrepo]

    elif change['new'] == 'PVsyst':
        inverter_vbox.children = [inverter_btn, dropdown_pvsyst]

    elif change['new'] == 'Manual':
        inverter_vbox.children = [inverter_btn, dropdown_manual]

def handle_dropdown_repo(change):
    if change['new'] == 'CECInverter':
        inv_drop = widgets.Dropdown(options=list(pvlib.pvsystem.retrieve_sam(change['new']).transpose().index),
                            value=None,
                            description='Inversores:',
                            style={'description_width': 'initial'})

        inverter_vbox.children = [inverter_btn, dropdown_invrepo, inv_drop]

    elif change['new'] == 'SandiaInverter':
        inv_drop = widgets.Dropdown(options=list(pvlib.pvsystem.retrieve_sam(change['new']).transpose().index),
                            value=None,
                            description='Inversores:',
                            style={'description_width': 'initial'})

        inverter_vbox.children = [inverter_btn, dropdown_invrepo, inv_drop]

    elif change['new'] == 'ADRInverter':
        inv_drop = widgets.Dropdown(options=list(pvlib.pvsystem.retrieve_sam(change['new']).transpose().index),
                            value=None,
                            description='Inversores:',
                            style={'description_width': 'initial'})

        inverter_vbox.children = [inverter_btn, dropdown_manual, inv_drop]

def handle_dropdown_manual(change):    
    if change['new'] == 'SNL PVlib':
        w_Paco = widgets.FloatText(value=None, description='Paco [W]', style={'description_width': 'initial'})
        w_Pdco = widgets.FloatText(value=None, description='Pdco [W]', style={'description_width': 'initial'})
        w_Vdco = widgets.FloatText(value=None, description='Vdco [V]', style={'description_width': 'initial'})
        w_Pso = widgets.FloatText(value=None, description='Pso [W]', style={'description_width': 'initial'})
        w_C0 = widgets.FloatText(value=None, description='C0 [1/W]', style={'description_width': 'initial'})
        w_C1 = widgets.FloatText(value=None, description='C1 [1/V]', style={'description_width': 'initial'})
        w_C2 = widgets.FloatText(value=None, description='C2 [1/V]', style={'description_width': 'initial'})
        w_C3 = widgets.FloatText(value=None, description='C3 [1/V]', style={'description_width': 'initial'})
        w_Pnt = widgets.FloatText(value=None, description='Pnt [W]', style={'description_width': 'initial'})

        inv_conf = widgets.VBox([widgets.HTML("<h5>Configuración SNL PVlib</h5>", layout=widgets.Layout(height='auto')),
                                 w_Paco, w_Pdco, w_Vdco, w_Pso, w_C0, w_C1, w_C2, w_C3, w_Pnt])

        inverter_vbox.children = [inverter_btn, dropdown_manual, inv_conf]

    elif change['new'] == 'NREL PVWatts':
        w_pdc0 = widgets.FloatText(value=None, description='pdc0 [W]', style={'description_width': 'initial'})
        w_eta_inv_nom = widgets.FloatText(value=None, description='eta_inv_nom [ad.]', style={'description_width': 'initial'})
        w_eta_inv_ref = widgets.FloatText(value=0.9637, description='eta_inv_ref [ad.]', style={'description_width': 'initial'})

        inv_conf = widgets.VBox([widgets.HTML("<h5>Configuración NREL PVWatts</h5>", layout=widgets.Layout(height='auto')),
                                 w_pdc0, w_eta_inv_nom, w_eta_inv_ref])

        inverter_vbox.children = [inverter_btn, dropdown_manual, inv_conf]

inverter_btn.observe(handle_toggle, 'value')
dropdown_invrepo.observe(handle_dropdown_repo, 'value')
dropdown_manual.observe(handle_dropdown_manual, 'value')

tab_inverter = widgets.Box([header, inverter_vbox], 
                            layout=widgets.Layout(display='flex',
                                          flex_flow='column',
                                          border='solid 0px',
                                          align_items='stretch',
                                          width='50%'))

# Module Tab
header = widgets.HTML("<h4>Método de Configuración</h4>", layout=widgets.Layout(height='auto'))

module_btn = widgets.ToggleButtons(value=None,
                                   options=['Repositorio', 'PVsyst', 'Manual'],
                                   description='',
                                   disabled=False,
                                   button_style='', # 'success', 'info', 'warning', 'danger' or ''
                                   tooltips=['Configuración desde bases de datos en PVlib', 
                                             'Configuración desde bases de datos en PVsyst', 
                                             'Configuración manual'])

module_vbox = widgets.VBox([module_btn])

dropdown_modrepo = widgets.Dropdown(options=mod_repo,
                                    value=None,
                                    description='Repositorio:',
                                    style={'description_width': 'initial'})

dropdown_pvsyst = widgets.Dropdown(options=['', 'pvmodule', 'cecmodule'],
                                   value=None,
                                   description='Repositorio:',
                                   style={'description_width': 'initial'})

def handle_toggle(change):
    if change['new'] == 'Repositorio':
        module_vbox.children = [module_btn, dropdown_modrepo]

    elif change['new'] == 'PVsyst':
        module_vbox.children = [module_btn, dropdown_pvsyst]

    elif change['new'] == 'Manual':

        w_BIPV = widgets.Text(value='N', description='BIPV', style={'description_width': 'initial'})
        w_T_NOCT = widgets.FloatText(value=None, description='T_NOCT', style={'description_width': 'initial'})
        w_A_c = widgets.FloatText(value=None, description='A_c', style={'description_width': 'initial'})
        w_N_s = widgets.FloatText(value=None, description='N_s', style={'description_width': 'initial'})
        w_I_sc_ref = widgets.FloatText(value=None, description='I_sc_ref', style={'description_width': 'initial'})
        w_V_oc_ref = widgets.FloatText(value=None, description='V_oc_ref', style={'description_width': 'initial'})
        w_I_mp_ref = widgets.FloatText(value=None, description='I_mp_ref', style={'description_width': 'initial'})
        w_V_mp_ref = widgets.FloatText(value=None, description='V_mp_ref', style={'description_width': 'initial'})
        w_alpha_sc = widgets.FloatText(value=None, description='alpha_sc', style={'description_width': 'initial'})
        w_beta_oc = widgets.FloatText(value=None, description='beta_oc', style={'description_width': 'initial'})
        w_a_ref = widgets.FloatText(value=None, description='a_ref', style={'description_width': 'initial'})
        w_I_L_ref = widgets.FloatText(value=None, description='I_L_ref', style={'description_width': 'initial'})
        w_I_o_ref = widgets.FloatText(value=None, description='I_o_ref', style={'description_width': 'initial'})
        w_R_s = widgets.FloatText(value=None, description='R_s', style={'description_width': 'initial'})
        w_R_sh_ref = widgets.FloatText(value=None, description='R_sh_ref', style={'description_width': 'initial'})
        w_Adjust = widgets.FloatText(value=None, description='Adjust', style={'description_width': 'initial'})
        w_gamma_r = widgets.FloatText(value=None, description='gamma_r', style={'description_width': 'initial'})
        w_PTC = widgets.FloatText(value=None, description='PTC', style={'description_width': 'initial'})
        w_pdc0 = widgets.FloatText(value=None, description='pdc0', style={'description_width': 'initial'})

        mod_conf = widgets.VBox([widgets.HTML("<h5>Configuración Módulo</h5>", layout=widgets.Layout(height='auto')),
                                 w_BIPV, w_T_NOCT, w_A_c, w_N_s,  w_I_sc_ref, w_V_oc_ref, w_I_mp_ref, w_V_mp_ref,
                                 w_alpha_sc, w_beta_oc, w_a_ref, w_I_L_ref, w_I_o_ref, w_R_s, w_R_sh_ref,
                                 w_Adjust, w_gamma_r, w_PTC, w_pdc0])

        module_vbox.children = [module_btn, mod_conf]

def handle_dropdown_repo(change):
    if change['new'] == 'CECMod':
        mod_drop = widgets.Dropdown(options=list(pvlib.pvsystem.retrieve_sam(change['new']).transpose().index),
                                    value=None,
                                    description='Módulos:',
                                    style={'description_width': 'initial'})

        module_vbox.children = [module_btn, dropdown_modrepo, mod_drop]

    elif change['new'] == 'SandiaMod':
        mod_drop = widgets.Dropdown(options=list(pvlib.pvsystem.retrieve_sam(change['new']).transpose().index),
                                    value=None,
                                    description='Módulos:',
                                    style={'description_width': 'initial'})

        module_vbox.children = [module_btn, dropdown_modrepo, mod_drop]

    elif change['new'] == 'PVFree':
        dropdown_pvfree = widgets.Dropdown(options=['', 'pvmodule', 'cecmodule'],
                                           value=None,
                                           description='Repositorio:',
                                           style={'description_width': 'initial'})

        mod_conf = widgets.VBox([widgets.IntText(value=None, description='ID', style={'description_width': 'initial'})])        

        module_vbox.children = [module_btn, dropdown_modrepo, dropdown_pvfree, mod_conf]

module_btn.observe(handle_toggle, 'value')
dropdown_modrepo.observe(handle_dropdown_repo, 'value')

tab_module = widgets.Box([header, module_vbox], 
                          layout=widgets.Layout(display='flex',
                                                flex_flow='column',
                                                border='solid 0px',
                                                align_items='stretch',
                                                width='50%'))

# System Configuration Tab
header1 = widgets.HTML("<h4>Orientación Módulos</h4>", layout=widgets.Layout(height='auto'))

tracker_btn = widgets.ToggleButtons(value=None,
                                    options=['Sin Seguidor', 'Seguidor 1-Eje', 'Seguidor 2-Eje'],
                                    description='',
                                    disabled=False,
                                    button_style='', # 'success', 'info', 'warning', 'danger' or ''
                                    tooltips=['Montaje con paneles estáticos', 
                                              'Montaje con paneles que rotan en un eje', 
                                              'Montaje con paneles que rotan en dos ejes'])

sysconfig_vbox = widgets.VBox([tracker_btn])

dropdown_repo = widgets.Dropdown(options=mod_repo,
                                 value=None,
                                 description='Repositorio:',
                                 style={'description_width': 'initial'})

dropdown_pvsyst = widgets.Dropdown(options=['', 'pvmodule', 'cecmodule'],
                                   value=None,
                                   description='Repositorio:',
                                   style={'description_width': 'initial'})

def handle_toggle(change):
    if change['new'] == 'Sin Seguidor':
        w_Azimuth = widgets.FloatText(value=None, description='Azimutal', style={'description_width': 'initial'})
        w_Tilt = widgets.FloatText(value=None, description='Elevación', style={'description_width': 'initial'})
        w_ModuleType = widgets.Dropdown(options=['open_rack_glass_glass', 'close_mount_glass_glass', 'open_rack_glass_polymer', 'insulated_back_glass_polymer'], value=None, description='Tipo Módulo', style={'description_width': 'initial'})

        no_tracker = widgets.VBox([widgets.HTML("<h5>Configuración Módulo</h5>", layout=widgets.Layout(height='auto')),
                                   w_Azimuth, w_Tilt, w_ModuleType])

        sysconfig_vbox.children = [tracker_btn, no_tracker]

    elif change['new'] == 'Seguidor 1-Eje':
        w_AxisTilt = widgets.FloatText(value=0, description='Elevación Eje', style={'description_width': 'initial'})
        w_AxisAzimuth = widgets.FloatText(value=180, description='Azimutal Eje', style={'description_width': 'initial'})
        w_MaxAngle = widgets.FloatText(value=None, description='Ángulo Máximo', style={'description_width': 'initial'})
        w_ModuleType = widgets.Dropdown(options=['open_rack_glass_glass', 'close_mount_glass_glass', 'open_rack_glass_polymer', 'insulated_back_glass_polymer'], value=None, description='Tipo Módulo', style={'description_width': 'initial'})
        w_Racking = widgets.Dropdown(options=['open_rack', 'close_mount', 'insulated_back'], value=None, description='Estructura Montaje', style={'description_width': 'initial'})
        w_Heigh = widgets.FloatText(value=None, description='Altura Módulo', style={'description_width': 'initial'})

        single_tracker = widgets.VBox([widgets.HTML("<h5>Configuración Módulo</h5>", layout=widgets.Layout(height='auto')),
                                 w_AxisTilt, w_AxisAzimuth, w_MaxAngle, w_ModuleType, w_Racking, w_Heigh])

        sysconfig_vbox.children = [tracker_btn, single_tracker]

    elif change['new'] == 'Seguidor 2-Eje':
        w_AxisTilt = widgets.FloatText(value=0, description='Elevación Eje', style={'description_width': 'initial'})
        w_AxisAzimuth = widgets.FloatText(value=180, description='Azimutal Eje', style={'description_width': 'initial'})
        w_MaxAngle = widgets.FloatText(value=None, description='Ángulo Máximo', style={'description_width': 'initial'})
        w_ModuleType = widgets.Dropdown(options=['open_rack_glass_glass', 'close_mount_glass_glass', 'open_rack_glass_polymer', 'insulated_back_glass_polymer'], value=None, description='Tipo Módulo', style={'description_width': 'initial'})
        w_Racking = widgets.Dropdown(options=['open_rack', 'close_mount', 'insulated_back'], value=None, description='Estructura Montaje', style={'description_width': 'initial'})
        w_Heigh = widgets.FloatText(value=None, description='Altura Módulo', style={'description_width': 'initial'})

        single_tracker = widgets.VBox([widgets.HTML("<h5>Configuración Módulo</h5>", layout=widgets.Layout(height='auto')),
                                 w_AxisTilt, w_AxisAzimuth, w_MaxAngle, w_ModuleType, w_Racking, w_Heigh])

        sysconfig_vbox.children = [tracker_btn, single_tracker]

def handle_dropdown_repo(change):
    if change['new'] == 'CECMod':
        mod_drop = widgets.Dropdown(options=list(pvlib.pvsystem.retrieve_sam(change['new']).transpose().index),
                                    value=None,
                                    description='Módulos:',
                                    style={'description_width': 'initial'})

        sysconfig_vbox.children = [tracker_btn, dropdown_repo, mod_drop]

    elif change['new'] == 'SandiaMod':
        mod_drop = widgets.Dropdown(options=list(pvlib.pvsystem.retrieve_sam(change['new']).transpose().index),
                                    value=None,
                                    description='Módulos:',
                                    style={'description_width': 'initial'})

        sysconfig_vbox.children = [tracker_btn, dropdown_repo, mod_drop]

    elif change['new'] == 'PVFree':
        dropdown_pvfree = widgets.Dropdown(options=['', 'pvmodule', 'cecmodule'],
                                           value=None,
                                           description='Repositorio:',
                                           style={'description_width': 'initial'})

        mod_conf = widgets.VBox([widgets.IntText(value=None, description='ID', style={'description_width': 'initial'})])        

        sysconfig_vbox.children = [tracker_btn, dropdown_repo, dropdown_pvfree, mod_conf]

tracker_btn.observe(handle_toggle, 'value')
dropdown_repo.observe(handle_dropdown_repo, 'value')

header2 = widgets.HTML("<h4>Configuración Eléctrica</h4>", layout=widgets.Layout(height='auto'))

n_arrays = widgets.FloatText(value=1, description='Número Arrays', style={'description_width': 'initial'})
mps = widgets.Text(value=None, description='Módulos por String', style={'description_width': 'initial'})
spi = widgets.Text(value=None, description='Strings por Inversor', style={'description_width': 'initial'})
n_inv = widgets.FloatText(value=1, description='Número Inversores', style={'description_width': 'initial'})

electric_config = widgets.VBox([n_arrays, mps, spi, n_inv])

header3 = widgets.HTML("<h4>Pérdidas</h4>", layout=widgets.Layout(height='auto'))

w_loss = widgets.FloatText(value=26.9, description='Pérdidas', style={'description_width': 'initial'})

tab_sysconfig = widgets.Box([header, sysconfig_vbox, header2, electric_config, header3, w_loss], 
                            layout=widgets.Layout(display='flex',
                                                  flex_flow='column',
                                                  border='solid 0px',
                                                  align_items='stretch',
                                                  width='50%'))


# Str List to List
def str_to_list(string):
    l = []
    l.append('[')
    l.append(string)
    l.append(']')

    return json.loads(''.join(l))

# Status Check
## Inverter
def check_inverter():
    if inverter_btn.value == 'Repositorio':
        inverters_database = dropdown_invrepo.value
        inverter_name = inverter_vbox.children[2].value
        inverter = None
        ac_model = 'sandia'

    if inverter_btn.value == 'Manual':
        if dropdown_manual.value == 'SNL PVlib':
            inverter = {'Paco': inverter_vbox.children[2].children[1].value,
                        'Pdco': inverter_vbox.children[2].children[2].value,
                        'Vdco': inverter_vbox.children[2].children[3].value,
                        'Pso': inverter_vbox.children[2].children[4].value,
                        'C0': inverter_vbox.children[2].children[5].value,
                        'C1': inverter_vbox.children[2].children[6].value,
                        'C2': inverter_vbox.children[2].children[7].value,
                        'C3': inverter_vbox.children[2].children[8].value,
                        'Pnt': inverter_vbox.children[2].children[9].value}

            ac_model = 'sandia'

        elif dropdown_manual.value == 'NREL PVWatts':
            inverter = {'pdc0': inverter_vbox.children[2].children[1].value,
                        'eta_inv_nom': inverter_vbox.children[2].children[2].value,
                        'eta_inv_ref': inverter_vbox.children[2].children[3].value}

            ac_model = 'pvwatts'

        inverters_database = None
        inverter_name = None

    return [inverters_database, inverter_name, inverter, ac_model]

## Module
def check_module():
    if module_btn.value == 'Repositorio':

        if dropdown_modrepo.value != 'PVFree':
            modules_database = dropdown_modrepo.value
            modules_name = module_vbox.children[2].value
            module = None

        else:
            modules_database = dropdown_modrepo.value
            module = requests.get(f'https://pvfree.herokuapp.com/api/v1/{module_vbox.children[2].value}/{module_vbox.children[3].children[0].value}/').json()
            modules_name = module['Name']           

    if module_btn.value == 'Manual':
        module = {'BIPV': module_vbox.children[1].children[1].value,
                  'T_NOCT': module_vbox.children[1].children[2].value,
                  'A_c': module_vbox.children[1].children[3].value,
                  'N_s': module_vbox.children[1].children[4].value,
                  'I_sc_ref': module_vbox.children[1].children[5].value,
                  'V_oc_ref': module_vbox.children[1].children[6].value,
                  'I_mp_ref': module_vbox.children[1].children[7].value,
                  'V_mp_ref': module_vbox.children[1].children[8].value,
                  'alpha_sc': module_vbox.children[1].children[9].value,
                  'beta_oc': module_vbox.children[1].children[10].value,
                  'a_ref': module_vbox.children[1].children[11].value,
                  'I_L_ref': module_vbox.children[1].children[12].value,
                  'I_o_ref': module_vbox.children[1].children[13].value,
                  'R_s': module_vbox.children[1].children[14].value,
                  'R_sh_ref': module_vbox.children[1].children[15].value,
                  'Adjust': module_vbox.children[1].children[16].value,
                  'gamma_r': module_vbox.children[1].children[17].value,
                  'PTC': module_vbox.children[1].children[18].value,
                  'pdc0': module_vbox.children[1].children[19].value}

        modules_database = None
        modules_name = None

    return [modules_database, modules_name, module]

## Mount
def check_mount():
    if tracker_btn.value == 'Sin Seguidor': 
        with_tracker = False
        tracker_axis = 0
        surface_azimuth = sysconfig_vbox.children[1].children[1].value
        surface_tilt = sysconfig_vbox.children[1].children[2].value
        axis_tilt = None
        axis_azimuth = None
        max_angle = None
        module_type = sysconfig_vbox.children[1].children[3].value
        racking_model = None
        module_height = None

    elif tracker_btn.value == 'Seguidor 1-Eje':
        with_tracker = True
        tracker_axis = 1
        surface_azimuth = None
        surface_tilt = None
        axis_tilt = sysconfig_vbox.children[1].children[1].value
        axis_azimuth = sysconfig_vbox.children[1].children[2].value
        max_angle = sysconfig_vbox.children[1].children[3].value
        module_type = sysconfig_vbox.children[1].children[4].value
        racking_model = sysconfig_vbox.children[1].children[5].value
        module_height = sysconfig_vbox.children[1].children[6].value

    elif tracker_btn.value == 'Seguidor 2-Eje':
        with_tracker = True
        tracker_axis = 2
        surface_azimuth = None
        surface_tilt = None
        axis_tilt = sysconfig_vbox.children[1].children[1].value
        axis_azimuth = sysconfig_vbox.children[1].children[2].value
        max_angle = sysconfig_vbox.children[1].children[3].value
        module_type = sysconfig_vbox.children[1].children[4].value
        racking_model = sysconfig_vbox.children[1].children[5].value
        module_height = sysconfig_vbox.children[1].children[6].value

    return [with_tracker, tracker_axis, surface_azimuth, surface_tilt, axis_tilt, axis_azimuth, max_angle, module_type, racking_model, module_height]

## Electric Configuration
def check_econfig(num_arrays):
    if num_arrays == 1:
        modules_per_string = int(mps.value) #Modules Per String
        strings_per_inverter = int(spi.value) #Strings Per Inverter  

    elif num_arrays > 1:
        modules_per_string = str_to_list(mps.value) #Modules Per String
        strings_per_inverter = str_to_list(spi.value) #Strings Per Inverter

    return [modules_per_string, strings_per_inverter]

## System Configuration
def sys_config(inverter_status, module_status, mount_status, econfig_status):
    system_configuration = {# Geographic Info
                            'latitude': w_latitude.value,
                            'longitude': w_longitude.value,
                            'tz': w_time_zone.value,
                            'altitude': w_altitude.value,
                            'surface_type': w_surface.value,
                            'surface_albedo': w_albedo.value,

                            # Inverter
                            'inverters_database': inverter_status[0],
                            'inverter_name': inverter_status[1],
                            'inverter': inverter_status[2],
                            'ac_model': inverter_status[3],

                            # PV Module
                            'modules_database': module_status[0],
                            'module_name': module_status[1],
                            'module': module_status[2],

                            # Mount
                            'with_tracker': mount_status[0],
                            'tracker_axis': mount_status[1],
                            'surface_azimuth': mount_status[2],
                            'surface_tilt': mount_status[3],
                            'axis_tilt': mount_status[4],
                            'axis_azimuth': mount_status[5],
                            'max_angle': mount_status[6],
                            'module_type': mount_status[7],
                            'racking_model': mount_status[8],
                            'module_height': mount_status[9],

                            # Electric Configuration
                            'num_arrays': n_arrays.value,
                            'num_inverter': n_inv.value,
                            'modules_per_string': econfig_status[0],
                            'strings_per_inverter': econfig_status[1],

                            # Loss
                            'loss': w_loss.value}

    return system_configuration

# GUI - Dashboard
item_layout = widgets.Layout(margin='0 0 25px 0')

tab = widgets.Tab([tab_location, tab_inverter, tab_module, tab_sysconfig], 
                  layout=item_layout)

tab.set_title(0, 'Ubicación')
tab.set_title(1, 'Inversor')
tab.set_title(2, 'Módulo')
tab.set_title(3, 'Configuración')
#display(tab)

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
        mount_status = check_mount()
        econfig_status = check_econfig(num_arrays=n_arrays.value)

        system_configuration = sys_config(inverter_status, module_status, mount_status, econfig_status)

        print('Configuración exitosa!')

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
        mount_status = check_mount()
        econfig_status = check_econfig(num_arrays=n_arrays.value)
        system_configuration = sys_config(inverter_status, module_status, mount_status, econfig_status)

        with open('system_config.json', 'w') as f:
            json.dump(system_configuration, f, indent=2)

        print('Descarga exitosa!')

download_btn.on_click(on_button_clicked)

btns = widgets.HBox([genconfig_btn, download_btn])
out_btns = widgets.HBox([genconfig_output, output])

dashboard = widgets.VBox([tab, btns, out_btns])
display(dashboard)