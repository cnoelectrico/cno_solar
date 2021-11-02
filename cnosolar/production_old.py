import pvlib
import pandas as pd
from functools import reduce

# DC Production
def dc_production(poa, cell_temperature, module, system):
    '''
    Docstrings
    '''
    # Single Diode Parameters
    IL, I0, Rs, Rsh, nNsVth = pvlib.pvsystem.calcparams_cec(effective_irradiance=poa,
                                                            temp_cell=cell_temperature,
                                                            alpha_sc=module['alpha_sc'],
                                                            a_ref=module['a_ref'],
                                                            I_L_ref=module['I_L_ref'],
                                                            I_o_ref=module['I_o_ref'],
                                                            R_sh_ref=module['R_sh_ref'],
                                                            R_s=module['R_s'],
                                                            Adjust=module['Adjust'],
                                                            EgRef=1.121,
                                                            dEgdT=-0.0002677)
    # Single Diode Equation
    curve_info = pvlib.pvsystem.singlediode(photocurrent=IL,
                                            saturation_current=I0,
                                            resistance_series=Rs,
                                            resistance_shunt=Rsh,
                                            nNsVth=nNsVth,
                                            ivcurve_pnts=100,
                                            method='lambertw')

    # Scalating Single Diode Results
    data_i_sc = pd.Series(curve_info['i_sc'])
    data_v_oc = pd.Series(curve_info['v_oc'])
    data_i_mp = pd.Series(curve_info['i_mp'])
    data_v_mp = pd.Series(curve_info['v_mp'])
    data_p_mp = pd.Series(curve_info['p_mp'])
    data_i_x = pd.Series(curve_info['i_x'])
    data_i_xx = pd.Series(curve_info['i_xx'])

    results_general = pd.DataFrame({'i_sc': data_i_sc, 
                                    'v_oc': data_v_oc,
                                    'i_mp': data_i_mp, 
                                    'v_mp': data_v_mp, 
                                    'p_mp': data_p_mp, 
                                    'i_x': data_i_x,
                                    'i_xx': data_i_xx})

    results_general = results_general.set_index(poa.index)
    
    # DC Production Dataframe
#     results = []
#     for i in range(num_arrays):
#         results.append(results_general)

#     dc = system.scale_voltage_current_power(tuple(results))
#     dc = system.scale_voltage_current_power(tuple(results_general))
    
    dc = system.scale_voltage_current_power(results_general)

    #     if num_arrays == 1:
#         dc = [dc]
#     else:
#         dc = list(dc)
    
    return dc

#     results = []
#     for i in range(num_arrays):
#         results.append(system.scale_voltage_current_power(results_general[i]))
#     dc = tuple(results)
    
#     return list(dc)

# Losses
def losses(dc, loss=26.9):

    losses = loss/100 #According to the paper Performance Parameters for Grid-Connected PV Systems by NREL

#     for i in range(len(dc)):
#         dc[i]['i_mp'] = dc[i]['i_mp'] - dc[i]['i_mp']*losses
#         dc[i]['p_mp'] = dc[i]['p_mp'] - dc[i]['p_mp']*losses

    dc['i_mp'] = dc['i_mp'] - dc['i_mp']*losses
    dc['p_mp'] = dc['p_mp'] - dc['p_mp']*losses
    
    return dc

# AC Power
## SAPM
def ac_production_sandia(dc, inverter, num_inverter=1, per_mppt=1):
    
#     ac_string = []
#     for i in range(len(dc)):
#         ac_string.append(pvlib.inverter.sandia(dc[i]['v_mp'], dc[i]['p_mp'], inverter))
    
#     ac = reduce(lambda a, b: a.add(b, fill_value=0), ac_string) * num_inverter

    ac = pvlib.inverter.sandia(dc['v_mp'], dc['p_mp'], inverter)
    ac = ac * num_inverter * per_mppt
    
    ac.loc[ac < 0] = 0
    ac.fillna(value=0, inplace=True)
    
    return ac


## PVWatts
def ac_production_pvwatts(dc, inverter, num_inverter=1, per_mppt=1):
    
#     ac_string = []
#     for i in range(len(dc)):
#         ac_string.append(pvlib.inverter.pvwatts(pdc=dc[i]['p_mp'], 
#                                                 pdc0=inverter['pdc0'],
#                                                 eta_inv_nom=inverter['eta_inv_nom'],
#                                                 eta_inv_ref=0.9637).fillna(0))
    
#     ac = reduce(lambda a, b: a.add(b, fill_value=0), ac_string) * num_inverter

    ac = pvlib.inverter.pvwatts(pdc=dc['p_mp'], 
                                pdc0=inverter['pdc0'],
                                eta_inv_nom=inverter['eta_inv_nom'],
                                eta_inv_ref=0.9637).fillna(0)
    
    ac = ac * num_inverter * per_mppt

    return ac

# Daily, Weekly, Monthly Energy
def get_energy(ac, resolution, energy_units='Wh'):    
    min_to_hour = resolution/60 #res is data resolution (1h, i.e. 60 min); 60 minutes equivalent to hour

    #Resampling Simulated Daily Energy
    ac_sim = ac*min_to_hour
    
    day_energy = pd.DataFrame(ac_sim.resample('1d').sum())
    day_energy.columns = ['energy']
    
    if energy_units == 'kWh':
        day_energy['energy'] = day_energy/1000
    if energy_units == 'MWh':
        day_energy['energy'] = day_energy/1000000

    day_energy = day_energy.resample('1d').max() #Daily energy
    
    week_energy = pd.DataFrame(day_energy.resample('1w').sum()) #Weekly energy
    week_energy.columns = ['energy']
    
    month_energy = pd.DataFrame(day_energy.resample('1m').sum()) #Monthly energy
    month_energy.columns = ['energy']
    
    #Energy Dataframes in Dictionary
    energy = {'day': day_energy, 'week': week_energy, 'month': month_energy} 
        
    return energy

# Production Pipeline
def production_pipeline(poa, cell_temperature, module, inverter, system, ac_model, loss, resolution, num_inverter=1, per_mppt=1, energy_units='Wh'):
    # DC Production
    dc = dc_production(poa, cell_temperature, module, system)

    # Losses
    dc = losses(dc, loss)

    # AC Production
    if ac_model == 'sandia':
        ac = ac_production_sandia(dc, inverter, num_inverter, per_mppt)

    if ac_model == 'pvwatts':
        ac = ac_production_pvwatts(dc, inverter, num_inverter, per_mppt)

    # Energy
    energy = get_energy(ac, resolution, energy_units)

    return dc, ac, energy