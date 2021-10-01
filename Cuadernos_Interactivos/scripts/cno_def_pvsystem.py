import pvlib

def get_arrays(num_arrays, array_name, mount, surface_type, module_type, module, mps, spi):

    temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm'][module_type]
    
    string_arrays = []
    for i in range(num_arrays):
        string_arrays.append(pvlib.pvsystem.Array(mount=mount, 
                                                  albedo=pvlib.irradiance.SURFACE_ALBEDOS[surface_type], 
                                                  surface_type=surface_type, 
                                                  module_type=module_type, 
                                                  module_parameters=module, 
                                                  temperature_model_parameters=temp_params, 
                                                  modules_per_string=mps[i], 
                                                  strings=spi[i],
                                                  name=array_name[i]))

    return string_arrays

def get_pvsystem(with_tracker, tracker, string_arrays, surface_tilt, surface_azimuth, surface_type, module_type, module, inverter, racking_model):

    temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm'][module_type]
    
    if with_tracker == False:
        system = pvlib.pvsystem.PVSystem(arrays=string_arrays, 
                                         surface_tilt=surface_tilt, 
                                         surface_azimuth=surface_azimuth, 
                                         albedo=pvlib.irradiance.SURFACE_ALBEDOS[surface_type], 
                                         surface_type=surface_type, 
                                         module_type=module_type, 
                                         module_parameters=module, 
                                         temperature_model_parameters=temp_params, 
                                         inverter_parameters=inverter, 
                                         racking_model=racking_model, 
                                         losses_parameters=None)

    if with_tracker == True:
        system = pvlib.pvsystem.PVSystem(arrays=string_arrays, 
                                         surface_tilt=tracker.surface_tilt, 
                                         surface_azimuth=tracker.surface_azimuth, 
                                         albedo=pvlib.irradiance.SURFACE_ALBEDOS[surface_type], 
                                         surface_type=surface_type, 
                                         module_type=module_type, 
                                         module_parameters=module, 
                                         temperature_model_parameters=temp_params, 
                                         inverter_parameters=inverter, 
                                         racking_model=racking_model, 
                                         losses_parameters=None)
        
    return system