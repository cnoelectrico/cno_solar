import pvlib
import pandas as pd
from functools import reduce

# DC Production
def dc_production(poa, cell_temperature, module, system):
    '''
    Wrapper that calculates the DC production parameters
    at maximum power point.
    
    Parameters
    ----------
    poa : numeric
        Plane-of-array irradiance in [W/m^2].

    cell_temperature : numeric
        Average cell temperature of cells within a module in [ºC].
        
    module : dict
        Technical parameters of the PV module.

    system : class
        PVlib PV System defined class. Used to scale the results
        according to the PV system architecture (i.e., electrical
        configuration of modules per string and strings per 
        inverter).

    Returns
    -------
    dc : pandas.DataFrame
        Data structure that contains the following parameters:
            1. i_sc - Short circuit current in [A].
            2. v_oc - Open circuit voltage in [V].
            3. i_mp -Current at maximum power point in [A].
            4. v_mp -Voltage at maximum power point in [V].
            5. p_mp -Power at maximum power point in [W].
            6. i_x -Current at V=0.5·Voc in [A].
            7. i_xx -Current at V=0.5·(Voc+Vmp) in [A].

    Notes
    -----
    The calculation procedure is:
        1. Calculate the five parameter values for the single diode equation 
        at effective irradiance and cell temperature using the CEC model. The
        five parameters are:
            1. Light-generated current in [A].
            2. Diode saturation current in [A].
            3. Series resistance in [Ohms].
            4. Shunt resistance in [Ohms].
            5. The product of the usual unitless diode ideality factor (n),
               number of cells in series (Ns), and cell thermal voltage at
               specified effective irradiance and cell temperature.    
        2. Solve the single-diode equation to obtain a photovoltaic I-V curve.
           The returned parameters are:
               1. i_sc - Short circuit current in [A].
               2. v_oc - Open circuit voltage in [V].
               3. i_mp -Current at maximum power point in [A].
               4. v_mp -Voltage at maximum power point in [V].
               5. p_mp -Power at maximum power point in [W].
               6. i_x -Current at V=0.5·Voc in [A].
               7. i_xx -Current at V=0.5·(Voc+Vmp) in [A].
        3. Scales the voltage, current and power according to the PV system 
        architecture (i.e., electrical configuration of modules per string 
        and strings per inverter).
    
    More details at: 
    https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.pvsystem.calcparams_cec.html
    https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.pvsystem.singlediode.html
    https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.pvsystem.scale_voltage_current_power.html
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
    dc = system.scale_voltage_current_power(results_general)
    
    return dc

# Losses
def losses(dc, loss=13.92):
    '''
    Add overall system losses to DC production.
    
    Parameters
    ----------
    dc : pandas.DataFrame
        Data structure that contains the following parameters:
            1. i_sc - Short circuit current in [A].
            2. v_oc - Open circuit voltage in [V].
            3. i_mp -Current at maximum power point in [A].
            4. v_mp -Voltage at maximum power point in [V].
            5. p_mp -Power at maximum power point in [W].
            6. i_x -Current at V=0.5·Voc in [A].
            7. i_xx -Current at V=0.5·(Voc+Vmp) in [A].

    loss : float, optional
        Overall system losses in [%].
        Default = 14.6

    Returns
    -------
    dc : pandas.DataFrame
        Data structure that contains the following parameters:
            1. i_sc - Short circuit current in [A].
            2. v_oc - Open circuit voltage in [V].
            3. i_mp -Current at maximum power point in [A].
            4. v_mp -Voltage at maximum power point in [V].
            5. p_mp -Power at maximum power point in [W].
            6. i_x -Current at V=0.5·Voc in [A].
            7. i_xx -Current at V=0.5·(Voc+Vmp) in [A].

    Notes
    -----
    The calculation procedure is:
        1. Add losses percentage value to the current at maximum power point,
           as samples values minus samples values times losses percentage.
        2. Add losses percentage value to the power at maximum power point,
           as samples values minus samples values times losses percentage.
           The procedure is equivalent as the product of voltage at maximum 
           power point and the current at maximum power point with added losses.

    References
    ----------
    B. Marion, J. Adelstein, K. Boyle, H. Hayden, B. Hammond, T. Fletcher, B. Canada, 
    D.Narang, A. Kimber, L. Mitchell, G. Rich & T. Townsend (2005). Performance parameters 
    for grid-connected PV systems. Conference Record of the IEEE Photovoltaic Specialists 
    Conference, pp. 1601–1606, doi: 10.1109/PVSC.2005.1488451.
    '''
    losses = loss/100 #According to the paper Performance Parameters for Grid-Connected PV Systems by NREL

    dc['i_mp'] = dc['i_mp'] - dc['i_mp']*losses
    dc['p_mp'] = dc['p_mp'] - dc['p_mp']*losses
    
    return dc

# AC Power
## SAPM
def ac_production_sandia(dc, inverter, num_inverter=1, per_mppt=1.0, availability=1.0):
    '''
    Convert DC power and voltage to AC power using Sandia’s 
    Grid-Connected PV Inverter model.
    
    Parameters
    ----------
    dc : pandas.DataFrame
            Data structure that contains the following parameters:
            1. i_sc - Short circuit current in [A].
            2. v_oc - Open circuit voltage in [V].
            3. i_mp -Current at maximum power point in [A].
            4. v_mp -Voltage at maximum power point in [V].
            5. p_mp -Power at maximum power point in [W].
            6. i_x -Current at V=0.5·Voc in [A].
            7. i_xx -Current at V=0.5·(Voc+Vmp) in [A].

    inverter : dict
        Technical parameters of the inverter.
        
    num_inverter : int, optional
        Number of inverters with exactly the same electrical configuration. 
        Used to scale the AC power.
        Default = 1

    per_mppt : float, optional
        Fraction of power handled by each input (e.g., 1/Number of Inputs 
        or 1/MPPT Number).
        Default = 1.0
        
    availability : float, optional
        Percentage value of availability per inverter set with the exact 
        same electrical configuration.
        Default = 1.0

    Returns
    -------
    ac : numeric
        AC power output in [W].

    Notes
    -----
    The calculation procedure is:
        1. Calculate the AC power using Sandia’s Grid-Connected PV Inverter model.
        2. Scales the AC power by the number of inverters, percentage of entrances
           and availability.
    
    More details at: https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.inverter.sandia.html
    '''
    ac = pvlib.inverter.sandia(dc['v_mp'], dc['p_mp'], inverter)
    ac = ac * num_inverter * per_mppt * availability
    
    ac.loc[ac < 0] = 0
    ac.fillna(value=0, inplace=True)
    
    return ac

## PVWatts
def ac_production_pvwatts(dc, inverter, num_inverter=1, per_mppt=1, availability=1):
    '''
    Convert DC power and voltage to AC power using NREL’s 
    PVWatts inverter model. 
    
    Parameters
    ----------
    dc : pandas.DataFrame
        Data structure that contains the following parameters:
            1. i_sc - Short circuit current in [A].
            2. v_oc - Open circuit voltage in [V].
            3. i_mp -Current at maximum power point in [A].
            4. v_mp -Voltage at maximum power point in [V].
            5. p_mp -Power at maximum power point in [W].
            6. i_x -Current at V=0.5·Voc in [A].
            7. i_xx -Current at V=0.5·(Voc+Vmp) in [A].

    inverter : dict
        Technical parameters of the inverter.
        
    num_inverter : int, optional
        Number of inverters with exactly the same electrical configuration. 
        Used to scale the AC power.
        Default = 1

    per_mppt : float, optional
        Fraction of power handled by each input (e.g., 1/Number of Inputs 
        or 1/MPPT Number).
        Default = 1.0
        
    availability : float, optional
        Percentage value of availability per inverter set with the exact 
        same electrical configuration.
        Default = 1.0

    Returns
    -------
    ac : numeric
        AC power output in [W].

    Notes
    -----
    The calculation procedure is:
        1. Calculate the AC power using NREL’s PVWatts inverter model.
        2. Scales the AC power by the number of inverters, percentage of entrances
           and availability.
    
    More details at: https://pvlib-python.readthedocs.io/en/latest/generated/pvlib.inverter.pvwatts.html
    '''
    ac = pvlib.inverter.pvwatts(pdc=dc['p_mp'], 
                                pdc0=inverter['pdc0'],
                                eta_inv_nom=inverter['eta_inv_nom'],
                                eta_inv_ref=0.9637).fillna(0)
    
    ac = ac * num_inverter * per_mppt * availability

    return ac

# Daily, Weekly, Monthly Energy
def get_energy(ac, resolution, energy_units='Wh'):
    '''
    Calculate energy production from AC power.
    
    Parameters
    ----------
    ac : numeric
        AC power output in [W].

    resolution : int
        Temporal resolution of time stamps of the historical data series 
        (e.g., 5 for five-minute resolution time stamps).
        
    energy_units : int, optional
        Energy units to scale the calculations. Used to allow adaptation 
        of the energy results report.
        Default = Wh

    Returns
    -------
    energy : dict
        Data structure that contains the following parameters:
            1. Daily energy in selected units. Default units in [Wh].
            2. Weekly energy in selected units. Default units in [Wh].
            3. Monthly energy in selected units. Default units in [Wh].

    Notes
    -----
    The calculation procedure is:
        1. Calculate the hourly energy as the product of the AC power and 
           the fraction of the resolution between sixty.
        2. Calculate the daily energy as the sum of the hourly energy per day
           using the pandas.resample function.
        3. Calculate the weekly energy as the sum of the daily energy per week
           using the pandas.resample function. 
        4. Calculate the monthly energy as the sum of the daily energy per month
           using the pandas.resample function.
           
    More details at: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html
    '''
    min_to_hour = resolution/60 #res is data resolution (1h, i.e. 60 min); 60 minutes equivalent to hour

    #Resampling Simulated Daily Energy
    ac_sim = ac*min_to_hour
    
    day_energy = pd.DataFrame(ac_sim.resample('1d').sum()) # Daily energy
    day_energy.columns = ['energy']
    
    if energy_units == 'kWh':
        day_energy['energy'] = day_energy/1000
    elif energy_units == 'MWh':
        day_energy['energy'] = day_energy/1000000
    
    week_energy = pd.DataFrame(day_energy.resample('1w').sum()) # Weekly energy
    week_energy.columns = ['energy']
    
    month_energy = pd.DataFrame(day_energy.resample('1m').sum()) # Monthly energy
    month_energy.columns = ['energy']
    
    #Energy Dataframes in Dictionary
    energy = {'day': day_energy, 'week': week_energy, 'month': month_energy} 
        
    return energy

# Production Pipeline
def production_pipeline(poa, cell_temperature, module, inverter, system, ac_model, resolution, loss=14.6, num_inverter=1, per_mppt=1, availability=1, energy_units='Wh'):
    '''
    Wrapper that executes the production stages of the PV system, 
    including system losses.
    
    Parameters
    ----------
    poa : numeric
        Plane-of-array irradiance in [W/m^2].

    cell_temperature : numeric
        Average cell temperature of cells within a module in [ºC].
        
    module : dict
        Technical parameters of the PV module.

    inverter : dict
        Technical parameters of the inverter.

    system : class
        PVlib PV System defined class. Used to scale the results
        according to the PV system architecture (i.e., electrical
        configuration of modules per string and strings per 
        inverter).
        
    ac_model : string
        Inverter model to be executed. Valid options are 'sandia' 
        and 'pvwatts'.
        
    resolution : int
        Temporal resolution of time stamps of the historical data series 
        (e.g., 5 for five-minute resolution time stamps).
        
    loss : float, optional
        Overall system losses in [%].
        Default = 14.6

    num_inverter : int, optional
        Number of inverters with exactly the same electrical configuration. 
        Used to scale the AC power.
        Default = 1

    per_mppt : float, optional
        Fraction of power handled by each input (e.g., 1/Number of Inputs 
        or 1/MPPT Number).
        Default = 1.0
        
    availability : float, optional
        Percentage value of availability per inverter set with the exact 
        same electrical configuration.
        Default = 1.0

    energy_units : string, optional
        Energy units to scale the calculations. Used to allow adaptation 
        of the energy results report.
        Default = Wh

    Returns
    -------
    dc : pandas.DataFrame
        Data structure that contains the following parameters:
            1. i_sc - Short circuit current in [A].
            2. v_oc - Open circuit voltage in [V].
            3. i_mp -Current at maximum power point in [A].
            4. v_mp -Voltage at maximum power point in [V].
            5. p_mp -Power at maximum power point in [W].
            6. i_x -Current at V=0.5·Voc in [A].
            7. i_xx -Current at V=0.5·(Voc+Vmp) in [A].
    
    ac : numeric
        AC power output in [W].
    
    energy : dict
        Data structure that contains the following parameters:
            1. Daily energy in selected units. Default units in [Wh].
            2. Weekly energy in selected units. Default units in [Wh].
            3. Monthly energy in selected units. Default units in [Wh].

    Notes
    -----
    The calculation procedure is:
        1. Calculate the DC production parameters at maximum power point.
        2. Add overall system losses to DC production..
        3. Convert DC power and voltage to AC power using an inverter model. 
        4. Calculate energy production from AC power.
           
    See also
    --------
    cno.production.dc_production
    cno.production.losses
    cno.production.ac_production_sandia
    cno.production.ac_production_pvwatts
    cno.production.get_energy
    '''
    # DC Production
    dc = dc_production(poa, cell_temperature, module, system)

    # Losses
    dc = losses(dc, loss)

    # AC Production
    if ac_model == 'sandia':
        ac = ac_production_sandia(dc, inverter, num_inverter, per_mppt, availability)

    if ac_model == 'pvwatts':
        ac = ac_production_pvwatts(dc, inverter, num_inverter, per_mppt, availability)

    # Energy
    energy = get_energy(ac, resolution, energy_units)

    return dc, ac, energy