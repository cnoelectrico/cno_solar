import pvlib

def get_arrays(mount, surface_albedo, surface_type, module_type, module, mps, spi):
    '''
    Docstring
    '''
    temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm'][module_type]
    
#     if num_arrays == 1:
    string_array = [pvlib.pvsystem.Array(mount=mount, 
                                         albedo=surface_albedo, 
                                         surface_type=surface_type, 
                                         module_type=module_type, 
                                         module_parameters=module, 
                                         temperature_model_parameters=temp_params, 
                                         modules_per_string=mps, 
                                         strings=spi)]
#     else:
#         string_arrays = []
#         for i in range(num_arrays):
#             string_arrays.append(pvlib.pvsystem.Array(mount=mount, 
#                                                       albedo=pvlib.irradiance.SURFACE_ALBEDOS[surface_type], 
#                                                       surface_type=surface_type, 
#                                                       module_type=module_type, 
#                                                       module_parameters=module, 
#                                                       temperature_model_parameters=temp_params, 
#                                                       modules_per_string=mps[i], 
#                                                       strings=spi[i],
#                                                       name=''))

    return string_array

def get_pvsystem(with_tracker, tracker, string_array, surface_tilt, surface_azimuth, surface_albedo, surface_type, module_type, module, inverter, racking_model):
    '''
    Docstring
    '''
    temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm'][module_type]
    
    if with_tracker == False:
        system = pvlib.pvsystem.PVSystem(arrays=string_array, 
                                         surface_tilt=surface_tilt, 
                                         surface_azimuth=surface_azimuth, 
                                         albedo=surface_albedo, 
                                         surface_type=surface_type, 
                                         module_type=module_type, 
                                         module_parameters=module, 
                                         temperature_model_parameters=temp_params, 
                                         inverter_parameters=inverter, 
                                         racking_model=racking_model, 
                                         losses_parameters=None)

    if with_tracker == True:
        system = pvlib.pvsystem.PVSystem(arrays=string_array, 
                                         surface_tilt=tracker.surface_tilt, 
                                         surface_azimuth=tracker.surface_azimuth, 
                                         albedo=surface_albedo, 
                                         surface_type=surface_type, 
                                         module_type=module_type, 
                                         module_parameters=module, 
                                         temperature_model_parameters=temp_params, 
                                         inverter_parameters=inverter, 
                                         racking_model=racking_model, 
                                         losses_parameters=None)
        
    return system