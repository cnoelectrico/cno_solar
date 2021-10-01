import pvlib

def get_tcell_sandia(poa, temp_air, wind_speed, temp_params):

    temp_cell = pvlib.temperature.sapm_cell(poa_global=poa, 
                                            temp_air=temp_air, 
                                            wind_speed=wind_speed, 
                                            a=temp_params['a'], 
                                            b=temp_params['b'], 
                                            deltaT=temp_params['deltaT'], 
                                            irrad_ref=1000.0)
    
    return temp_cell

def get_tcell_tnoct(poa, temp_air, tnoct):
    
    temp_cell = temp_air + ((tnoct - 20)/800)*poa
    
    return temp_cell