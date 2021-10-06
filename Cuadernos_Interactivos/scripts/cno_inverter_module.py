import pvlib

def get_inv_mod(inverter_name, module_name, eta_inv_nom, inverters_database='CECInverter', modules_database='CECMod'):
    
    inverter = pvlib.pvsystem.retrieve_sam(inverters_database)[inverter_name]
    module = pvlib.pvsystem.retrieve_sam(modules_database)[module_name]
    
    # PVWatts Required Parameters
    inverter['pdc0'] = inverter['Pdco']
    inverter['eta_inv_nom'] = eta_inv_nom
    
    module['gamma_r'] = module['gamma_r']/100
    
    return inverter, module

def get_inverter(inverters_database, inverter_name, inv=None):
    if inv != None:
        inverter = inv
    else:
        inverter = pvlib.pvsystem.retrieve_sam(inverters_database)[inverter_name]
    
    # PVWatts Required Parameters
#     inverter['pdc0'] = inverter['Pdco']
#     inverter['eta_inv_nom'] = eta_inv_nom
    
    return inverter

def get_module(modules_database, module_name, mod=None):
    if mod != None:
        module = mod
    else:
        module = pvlib.pvsystem.retrieve_sam(modules_database)[module_name]
        
    module['gamma_r'] = module['gamma_r']/100
    
    return module