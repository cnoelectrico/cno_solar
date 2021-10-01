import sys  
sys.path.insert(0, './scripts')

import cno_libraries
get_ipython().run_line_magic('run', "-i './scripts/cno_libraries.py'")

import cno_meteorology
import cno_decomposition_transposition
import cno_inverter_module
import cno_singletracker
import cno_def_pvsystem
import cno_cell_temperature
import cno_production

def full_pipeline(system_configuration, data, resolution, energy_units):
    sc = system_configuration
    
    # Meteorological Data
    location, solpos, airmass, etr_nrel = cno_meteorology.get_meteo(sc['latitude'], 
                                                                    sc['longitude'], 
                                                                    sc['tz'], 
                                                                    sc['altitude'], 
                                                                    datetime=data.index)
    
    
    # Decomposition
    disc = cno_decomposition_transposition.decomposition(ghi=data.GHI, 
                                                         solpos=solpos, 
                                                         datetime=data.index)
    
    # Mount
    if sc['with_tracker'] == False:
        mount = cno_inverter_module.get_mount(sc['surface_tilt'], 
                                              sc['surface_azimuth'], 
                                              sc['racking_model'], 
                                              sc['module_height'])
        
        tracker = None
    
    elif sc['with_tracker'] == True:
        tracker, mount = cno_singletracker.get_tracker(solpos, 
                                                       sc['axis_tilt'], 
                                                       sc['axis_azimuth'], 
                                                       sc['max_angle'], 
                                                       sc['racking_model'], 
                                                       sc['module_height'], 
                                                       sc['with_tracker'])
        
    
    # Transposition
    poa = cno_decomposition_transposition.transposition(sc['surface_tilt'], 
                                                        sc['surface_azimuth'], 
                                                        solpos=solpos, 
                                                        disc=disc, 
                                                        ghi=data.GHI, 
                                                        etr_nrel=etr_nrel, 
                                                        airmass=airmass, 
                                                        surface_type=sc['surface_type'])
    
    # Inverter
    inverter = cno_inverter_module.get_inverter(sc['inverters_database'], 
                                                sc['inverter_name'], 
                                                inv=sc['inverter'])
    
    # Module
    module = cno_inverter_module.get_module(sc['modules_database'], 
                                            sc['module_name'], 
                                            mod=sc['module'])    
    
    # Arrays
    string_arrays = cno_def_pvsystem.get_arrays(sc['num_arrays'], 
                                                mount=mount, 
                                                surface_type=sc['surface_type'], 
                                                module_type=sc['module_type'], 
                                                module=pvlib.irradiance.SURFACE_ALBEDOS[surface_type], 
                                                mps=sc['modules_per_string'], 
                                                spi=sc['strings_per_inverter'])
    
    # PV System
    system = cno_def_pvsystem.get_pvsystem(string_arrays=string_arrays, 
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
