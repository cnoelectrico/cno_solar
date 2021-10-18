import pvlib

def from_sandia(poa, temp_air, wind_speed, temp_params):
    '''
    Docstring
    https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.temperature.sapm_cell.html#pvlib.temperature.sapm_cell
    '''
    temp_cell = pvlib.temperature.sapm_cell(poa_global=poa, 
                                            temp_air=temp_air, 
                                            wind_speed=wind_speed, 
                                            a=temp_params['a'], 
                                            b=temp_params['b'], 
                                            deltaT=temp_params['deltaT'], 
                                            irrad_ref=1000.0)
    
    return temp_cell

def from_tnoct(poa, temp_air, tnoct, mount_temp=0):
    '''
    Docstring
    tnoct
    tinoct (Solar Energy The Physics and Engineering of Photovoltaic Conversion, pp. 54)
    '''
    if mount_temp != None:
        temp_cell = temp_air + ((tnoct - 20)/800)*poa
    else:
        tinoct = tnoct - mount_temp
        temp_cell = temp_air + ((tinoct - 20)/800)*poa
    
    return temp_cell

def from_tmod(poa, temp_mod, temp_params):
    '''
    Docstring
    https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.temperature.sapm_cell_from_module.html#pvlib.temperature.sapm_cell_from_module
    '''
    temp_cell = pvlib.temperature.sapm_cell_from_module(module_temperature=temp_mod, 
                                                        poa_global=poa, 
                                                        deltaT=temp_params['deltaT'], 
                                                        irrad_ref=1000.0)
    
    return temp_cell

def from_pvsyst(poa, temp_air, wind_speed, u_c=29.0, u_v=0.0, eta_m=None, eta=0.1, alpha=0.9):
    '''
    https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.temperature.pvsyst_cell.html#pvlib.temperature.pvsyst_cell
    '''
    temp_cell = pvlib.temperature.pvsyst_cell(poa_global, 
                                              temp_air, 
                                              wind_speed=1.0,
                                              u_c=29.0, 
                                              u_v=0.0, 
                                              eta_m=None, 
                                              module_efficiency=eta, 
                                              alpha_absorption=alpha)
    
    return temp_cell

def from_sam(poa, temp_air, wind_speed, tnoct, eta, eff_irrad=None, transmittance=0.9, height=1, standoff=4):
    '''
    Docstring
    https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.temperature.noct_sam.html#pvlib.temperature.noct_sam
    '''
    temp_cell = pvlib.temperature.noct_sam(poa_global=poa, 
                                           temp_air=temp_air, 
                                           wind_speed=wind_speed, 
                                           noct=tnoct, 
                                           module_efficiency=eta, 
                                           effective_irradiance=eff_irrad, 
                                           transmittance_absorptance=transmittance, 
                                           array_height=height, 
                                           mount_standoff=standoff)
    
    return temp_cell
