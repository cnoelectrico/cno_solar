import sys  
sys.path.insert(0, './scripts')

import cno_libraries
from IPython import get_ipython
get_ipython().run_line_magic('run', "-i './scripts/cno_libraries.py'")

import cno_meteorology
import cno_decomposition_transposition
import cno_inverter_module
import cno_mount_tracker
import cno_def_pvsystem
import cno_cell_temperature
import cno_production

def full_pipeline(system_configuration, data, resolution, energy_units):
    sc = system_configuration
    
    # Meteorological Data
    location, solpos, airmass, etr_nrel = cno_meteorology.get_meteo(latitude=sc['latitude'], 
                                                                    longitude=sc['longitude'], 
                                                                    tz=sc['tz'], 
                                                                    altitude=sc['altitude'], 
                                                                    datetime=data.index)
    
    # Decomposition
    disc = cno_decomposition_transposition.decomposition(ghi=data.GHI, 
                                                         solpos=solpos, 
                                                         datetime=data.index)
    
    # Mount and Tracker
    mount, tracker = cno_mount_tracker.get_mount_tracker(with_tracker=sc['with_tracker'], 
                                                         surface_tilt=sc['surface_tilt'], 
                                                         surface_azimuth=sc['surface_azimuth'], 
                                                         solpos=solpos, 
                                                         axis_tilt=sc['axis_tilt'], 
                                                         axis_azimuth=sc['axis_azimuth'], 
                                                         max_angle=sc['max_angle'], 
                                                         tracker_axis=sc['tracker_axis'], # ACTUALIZARRRR!!!
                                                         racking_model='open_rack', 
                                                         module_height=None)
    
    # Transposition
    poa = cno_decomposition_transposition.transposition(with_tracker=sc['with_tracker'], 
                                                        tracker=tracker, 
                                                        surface_tilt=sc['surface_tilt'], 
                                                        surface_azimuth=sc['surface_azimuth'], 
                                                        solpos=solpos, 
                                                        disc=disc, 
                                                        ghi=data.GHI, # ACTUALIZARRRR!!! 
                                                        etr_nrel=etr_nrel, 
                                                        airmass=airmass, 
                                                        surface_type=sc['surface_type'])
    
    # Inverter
    inverter = cno_inverter_module.get_inverter(inverters_database=sc['inverters_database'], 
                                                inverter_name=sc['inverter_name'], 
                                                inv=sc['inverter'])
    
    # Module
    module = cno_inverter_module.get_module(modules_database=sc['modules_database'], 
                                            module_name=sc['module_name'], 
                                            mod=sc['module'])    
    
    # Arrays
    string_arrays = cno_def_pvsystem.get_arrays(num_arrays=sc['num_arrays'],
                                                mount=mount, 
                                                surface_type=sc['surface_type'], 
                                                module_type=sc['module_type'], 
                                                module=module, 
                                                mps=sc['modules_per_string'], 
                                                spi=sc['strings_per_inverter'])
#                                                 array_name=['SysA'], # ACTUALIZARRRR!!!
    
    # PV System
    system = cno_def_pvsystem.get_pvsystem(with_tracker=sc['with_tracker'], 
                                           tracker=tracker, 
                                           string_arrays=string_arrays, 
                                           surface_tilt=sc['surface_tilt'], 
                                           surface_azimuth=sc['surface_azimuth'], 
                                           surface_type=sc['surface_type'], 
                                           module_type=sc['module_type'], 
                                           module=module, 
                                           inverter=inverter, 
                                           racking_model=sc['racking_model'])
    
    # Cell Temperature
    temp_cell = cno_cell_temperature.get_tcell_tnoct(poa=poa.poa_global, 
                                                     temp_air=data['Temperature'], 
                                                     tnoct=module['T_NOCT'])
    
    # DC Production, AC Power and Energy
    dc, ac, energy = cno_production.production_pipeline(poa=poa.poa_global, 
                                                        cell_temperature=temp_cell, 
                                                        module=module, 
                                                        inverter=inverter, 
                                                        system=system, 
                                                        num_arrays=sc['num_arrays'], 
                                                        ac_model=sc['ac_model'], 
                                                        loss=sc['loss'], 
                                                        resolution=resolution, 
                                                        num_inverter=sc['num_inverter'], 
                                                        energy_units=energy_units)

    bus_pipeline = {'location': location, 
                    'solpos': solpos, 
                    'airmass': airmass, 
                    'etr_nrel': etr_nrel,
                    'disc': disc,
                    'tracker': tracker, 
                    'mount': mount,
                    'poa': poa,
                    'inverter': inverter,
                    'module': module,
                    'string_arrays': string_arrays,
                    'system': system,
                    'temp_cell': temp_cell,
                    'dc': dc, 
                    'ac': ac, 
                    'energy': energy}
    
    return bus_pipeline
