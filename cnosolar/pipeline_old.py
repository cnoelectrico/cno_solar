import cnosolar as cno
from functools import reduce

def run(system_configuration, data, num_subarrays, resolution, energy_units):
    '''
    Docstrings
    '''
    sc = system_configuration
    
    bus_pipeline = {}
    for i in range(num_subarrays):
        # Meteorological Data
        location, solpos, airmass, etr_nrel = cno.location_data.get_parameters(latitude=sc['latitude'], 
                                                                               longitude=sc['longitude'], 
                                                                               tz=sc['tz'], 
                                                                               altitude=sc['altitude'], 
                                                                               datetime=data.index)

        # Decomposition
        disc = cno.irradiance_models.decomposition(ghi=data.GHI, 
                                                   solpos=solpos, 
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
                                                           racking_model=sc['racking_model'], 
                                                           module_height=sc['module_height'])

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
        temp_cell = cno.cell_temperature.from_tnoct(poa=poa.poa_global, 
                                                    temp_air=data['Temperature'], 
                                                    tnoct=sc['module']['T_NOCT'])

        # DC Production, AC Power and Energy
        dc, ac, energy = cno.production.production_pipeline(poa=poa.poa_global, 
                                                            cell_temperature=temp_cell, 
                                                            module=sc['module'], 
                                                            inverter=sc['inverter'], 
                                                            system=system, 
                                                            ac_model=sc['ac_model'], 
                                                            loss=sc['loss'], 
                                                            resolution=resolution, 
                                                            num_inverter=sc['num_inverter'],
                                                            per_mppt=sc['per_mppt'][i],
                                                            energy_units=energy_units)

        if num_subarrays > 1:
            key = f'subarray_{i+1}'
        else:
            key = 'system'
            
        bus_pipeline[key] = {'location': location, 
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
    
    # AC and Energy Adition for Full System
    if num_subarrays > 1:
        ac_string = []
        denergy_string = []
        wenergy_string = []
        menergy_string = []
        for i in range(len(bus_pipeline.keys())):
            ac_string.append(bus_pipeline[f'subarray_{i+1}']['ac'])
            denergy_string.append(bus_pipeline[f'subarray_{i+1}']['energy']['day'].energy)
            wenergy_string.append(bus_pipeline[f'subarray_{i+1}']['energy']['week'].energy)
            menergy_string.append(bus_pipeline[f'subarray_{i+1}']['energy']['month'].energy)

        sys_ac = reduce(lambda a, b: a.add(b, fill_value=0), ac_string)
        sys_denergy = reduce(lambda a, b: a.add(b, fill_value=0), denergy_string)
        sys_wenergy = reduce(lambda a, b: a.add(b, fill_value=0), wenergy_string)
        sys_menergy = reduce(lambda a, b: a.add(b, fill_value=0), menergy_string)

        bus_pipeline['system'] = {'location': location, 
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