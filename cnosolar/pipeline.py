import numpy as np
import pandas as pd
import cnosolar as cno
from tqdm.auto import tqdm
from functools import reduce

def run(system_configuration, data, availability, energy_units):
    '''
    Docstrings
    '''
    bus_pipeline = {}
    num_systems = len(system_configuration)
    
    resolution = data.index.to_series().diff().median().total_seconds()/60
    
    if availability == None:
        inv_availability = list(np.repeat(1, num_systems))
    else:
        inv_availability = availability
    
    for j in tqdm(range(num_systems), desc='Sistema/Inversor (.JSON)', leave=False):
        sc = system_configuration[j]
        num_subarrays = sc['num_arrays']
        
        if num_systems > 1:
            superkey = f'inverter{j+1}'
        else:
            superkey = 'plant'
            
        bus_pipeline[superkey] = {}
        
        for i in tqdm(range(num_subarrays), desc='Subarrays', leave=False):
            # Meteorological Data
            location, solpos, airmass, etr_nrel = cno.location_data.get_parameters(latitude=sc['latitude'], 
                                                                                   longitude=sc['longitude'], 
                                                                                   tz=sc['tz'], 
                                                                                   altitude=sc['altitude'], 
                                                                                   datetime=data.index)

            # Mount and Tracker
            if sc['with_tracker'] == False:
                sur_tilt = sc['surface_tilt'][i]
                sur_azimuth = sc['surface_azimuth'][i]
                ax_tilt = None
                ax_azimuth = None
                m_angle = None
            else:
                sur_tilt = None
                sur_azimuth = None
                ax_tilt = sc['axis_tilt'][i]
                ax_azimuth = sc['axis_azimuth'][i]
                m_angle = sc['max_angle'][i]

            mount, tracker = cno.pvstructure.get_mount_tracker(with_tracker=sc['with_tracker'], 
                                                               surface_tilt=sur_tilt, 
                                                               surface_azimuth=sur_azimuth, 
                                                               solpos=solpos, 
                                                               axis_tilt=ax_tilt, 
                                                               axis_azimuth=ax_azimuth, 
                                                               max_angle=m_angle,
                                                               racking_model=sc['racking_model'])
            
            # POA Irradiance
            if list(data.columns)[0] == 'POA':
                
                disc = pd.DataFrame(data={'disc': list(np.repeat(0, len(data)))}, index=data.index)
                poa = data['POA']
            
            else:
                # Decomposition
                disc = cno.irradiance_models.decomposition(ghi=data['GHI'], 
                                                           solpos=solpos, 
                                                           datetime=data.index) 

                # Transposition
                poa = cno.irradiance_models.transposition(with_tracker=sc['with_tracker'], 
                                                          tracker=tracker, 
                                                          surface_tilt=sur_tilt, 
                                                          surface_azimuth=sur_azimuth, 
                                                          solpos=solpos, 
                                                          disc=disc, 
                                                          ghi=data['GHI'],
                                                          etr_nrel=etr_nrel, 
                                                          airmass=airmass,
                                                          surface_albedo=sc['surface_albedo'],
                                                          surface_type=sc['surface_type'])
                poa = poa.poa_global

            # Arrays
            string_array = cno.def_pvsystem.get_arrays(mount=mount,
                                                       surface_albedo=sc['surface_albedo'],
                                                       surface_type=sc['surface_type'], 
                                                       module_type=sc['module_type'], 
                                                       module=sc['module'], 
                                                       mps=sc['modules_per_string'][i], 
                                                       spi=sc['strings_per_inverter'][i])

            # PV System
            system = cno.def_pvsystem.get_pvsystem(with_tracker=sc['with_tracker'], 
                                                   tracker=tracker, 
                                                   string_array=string_array, 
                                                   surface_tilt=sur_tilt, 
                                                   surface_azimuth=sur_azimuth,
                                                   surface_albedo=sc['surface_albedo'],
                                                   surface_type=sc['surface_type'], 
                                                   module_type=sc['module_type'], 
                                                   module=sc['module'], 
                                                   inverter=sc['inverter'], 
                                                   racking_model=sc['racking_model'])
            
            # Cell Temperature
            if list(data.columns)[1] == 'Tmod':
                temp_cell = data['Tmod']
            
            else:
                temp_cell = cno.cell_temperature.from_tnoct(poa=poa, 
                                                            temp_air=data['Tamb'], 
                                                            tnoct=sc['module']['T_NOCT'])

            # DC Production, AC Power and Energy
            dc, ac, energy = cno.production.production_pipeline(poa=poa, 
                                                                cell_temperature=temp_cell, 
                                                                module=sc['module'], 
                                                                inverter=sc['inverter'], 
                                                                system=system, 
                                                                ac_model=sc['ac_model'], 
                                                                loss=sc['loss'], 
                                                                resolution=resolution, 
                                                                num_inverter=sc['num_inverter'],
                                                                per_mppt=sc['per_mppt'][i],
                                                                availability=inv_availability[j],
                                                                energy_units=energy_units)

            if num_subarrays > 1:
                key = f'subarray{i+1}'
            else:
                key = 'system'
            
            bus_pipeline[superkey][key] = {'location': location, 
                                           'solpos': solpos, 
                                           'airmass': airmass, 
                                           'etr_nrel': etr_nrel,
                                           'disc': disc,
                                           'tracker': tracker, 
                                           'mount': mount,
                                           'poa': poa,
                                           'string_array': string_array,
                                           'system': system,
                                           'temp_cell': temp_cell,
                                           'dc': dc, 
                                           'ac': ac, 
                                           'energy': energy}
    
        # AC and Energy Adition for Inverter
        if num_subarrays > 1:
            ac_string = []
            denergy_string = []
            wenergy_string = []
            menergy_string = []
            
            for i in range(num_subarrays):
                ac_string.append(bus_pipeline[superkey][f'subarray{i+1}']['ac'])
                denergy_string.append(bus_pipeline[superkey][f'subarray{i+1}']['energy']['day'].energy)
                wenergy_string.append(bus_pipeline[superkey][f'subarray{i+1}']['energy']['week'].energy)
                menergy_string.append(bus_pipeline[superkey][f'subarray{i+1}']['energy']['month'].energy)

            sys_ac = reduce(lambda a, b: a.add(b, fill_value=0), ac_string)
            sys_denergy = reduce(lambda a, b: a.add(b, fill_value=0), denergy_string)
            sys_wenergy = reduce(lambda a, b: a.add(b, fill_value=0), wenergy_string)
            sys_menergy = reduce(lambda a, b: a.add(b, fill_value=0), menergy_string)
                
            bus_pipeline[superkey]['system'] = {'location': location, 
                                                'solpos': solpos, 
                                                'airmass': airmass, 
                                                'etr_nrel': etr_nrel,
                                                'disc': disc,
                                                'tracker': tracker, 
                                                'mount': mount,
                                                'poa': poa,
                                                'temp_cell': temp_cell,
                                                'dc': dc, 
                                                'ac': sys_ac, 
                                                'energy': {'day': sys_denergy,
                                                           'week': sys_wenergy,
                                                           'month': sys_menergy}}
            
            
    # AC and Energy Adition for System
    if len(system_configuration) > 1:
        ac_inv = []
        denergy_inv = []
        wenergy_inv = []
        menergy_inv = []

        for i in range(len(system_configuration)):
            ac_inv.append(bus_pipeline[f'inverter{i+1}']['system']['ac'])
            denergy_inv.append(bus_pipeline[f'inverter{i+1}']['system']['energy']['day'])
            wenergy_inv.append(bus_pipeline[f'inverter{i+1}']['system']['energy']['week'])
            menergy_inv.append(bus_pipeline[f'inverter{i+1}']['system']['energy']['month'])

        sys_ac = reduce(lambda a, b: a.add(b, fill_value=0), ac_inv)
        sys_denergy = reduce(lambda a, b: a.add(b, fill_value=0), denergy_inv)
        sys_wenergy = reduce(lambda a, b: a.add(b, fill_value=0), wenergy_inv)
        sys_menergy = reduce(lambda a, b: a.add(b, fill_value=0), menergy_inv)

        bus_pipeline['plant'] = {'location': location, 
                                 'solpos': solpos, 
                                 'airmass': airmass, 
                                 'etr_nrel': etr_nrel,
                                 'disc': disc,
                                 'tracker': tracker, 
                                 'mount': mount,
                                 'poa': poa,
                                 'temp_cell': temp_cell,
                                 'dc': dc, 
                                 'ac': sys_ac, 
                                 'energy': {'day': sys_denergy,
                                            'week': sys_wenergy,
                                            'month': sys_menergy}}
    
    return bus_pipeline
    