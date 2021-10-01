import numpy as np
import pandas as pd
from calendar import monthrange

units = {'kWh': 1000, 'MWh': 1000000}

def enficc_creg(df, Kinc, IHF, CEN, a, b, c, d, Kmedt):
    efirme = df.copy()
    
    Istc = 1 # kW/m2
    Kc = 0.9139
    Fcu = 1000
    
    # Step 1: Losses due to ambient temperature
    efirme['Vmt_TAmt'] = 1 - (a*efirme['Temperature']**3 + b*efirme['Temperature']**2 + c*efirme['Temperature'] + d)
    
    # Step 2: Monthly energy estimate
    efirme['ENmt'] = (1/Istc) * Kc * Kinc * efirme['Vmt_TAmt'] * efirme['Insolation'] * (1 - IHF) * CEN * Fcu # kWh/month
    
    # Step 3: Daily energy estimate
    En = []
    for i in range(len(efirme)):
        En.append(efirme['ENmt'][i] / monthrange(efirme.index[i].year, efirme.index[i].month)[1])

    efirme['En'] = En # kWh/day

    # Step 4: ENFICC
    enficc = np.min(efirme['En']) # kWh/day
    
    # Step 5: Use factor of actual irradiance and degradation measurements
    enficc_t = np.round(enficc * Kmedt, 2) # kWh/day
    print('ENFICC [kWh/día] -- CREG 201 de 2017 =', enficc_t)
    
    return efirme, enficc_t

def efirme_pvlib_creg(energy):
    '''
    1. Energía mensual de PVlib
    2. Energía diaria según CREG 201 de 2017
    3. Energía Firme según CREG 201 de 2017 sin incluir Kmedt
    '''
    # Step 1: Daily energy estimate
    En = []
    for i in range(len(energy['month'])):
        e_kWh = energy['month']['energy'][i] / 1000 # kWh
        En.append(e_kWh / monthrange(energy['month'].index[i].year, energy['month'].index[i].month)[1])

    efirme = energy['month'].copy()
    efirme['En'] = En
    
    # Step 2: "ENFICC"
    enficc = np.round(np.min(efirme['En']), 2) # kWh/day
    print('ENFI [kWh/día] -- Mín(Energía Mes PVlib / Días) =', enficc)
    
    return efirme, enficc

def efirme_pvlib_min(energy):
    '''
    1. Energía diaria de PVlib
    2. Energía Firme como valor mínimo de energía diaria
    '''
    enficc = np.round(np.min(energy['daily']['energy'].loc[energy['daily']['energy'] != 0]) / 1000, 2) # kWh
    print('ENFI [kWh/día] -- Mín(Energía Día PVlib) =', enficc)
    return enficc

def efirme_pvlib_percentile(energy, percentile):
    '''
    1. Energía diaria de PVlib
    2. Energía Firme como percentil de energía diaria
    '''
    enficc = np.round(np.percentile(energy['daily']['energy'].loc[energy['daily']['energy'] != 0], percentile) / 1000, 2) # kWh
    print('ENFI [kWh/día] -- Percentil(Energía Día PVlib) =', enficc)
    return enficc