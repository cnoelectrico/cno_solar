import pvlib
from pvlib import irradiance
import numpy as np

# Decomposition Model: DISC
def decomposition(ghi, solpos, datetime):
    disc = pvlib.irradiance.disc(ghi=ghi, 
                                 solar_zenith=solpos.zenith, 
                                 datetime_or_doy=datetime, 
                                 pressure=None, # Absolute Airmass: 101325, Relative Airmass: None
                                 min_cos_zenith=0.065, # Default
                                 max_zenith=87, # Default
                                 max_airmass=12) # Default

    disc['dhi'] = ghi - disc.dni*np.cos(np.radians(solpos.zenith))

    return disc

# Transposition Model: Perez-Ineichen 1990
def transposition(with_tracker, tracker, surface_tilt, surface_azimuth, solpos, disc, ghi, etr_nrel, airmass, surface_type):
    if with_tracker == False:
        poa = pvlib.irradiance.get_total_irradiance(surface_tilt=surface_tilt, 
                                                    surface_azimuth=surface_azimuth, 
                                                    solar_zenith=solpos.zenith, 
                                                    solar_azimuth=solpos.azimuth, 
                                                    dni=disc.dni, 
                                                    ghi=ghi, 
                                                    dhi=disc.dhi, 
                                                    dni_extra=etr_nrel, 
                                                    airmass=airmass.airmass_relative, 
                                                    albedo=irradiance.SURFACE_ALBEDOS[surface_type], 
                                                    surface_type=surface_type, 
                                                    model='perez', 
                                                    model_perez='allsitescomposite1990')
    
    if with_tracker == True:
        poa = pvlib.irradiance.get_total_irradiance(surface_tilt=tracker.surface_tilt, 
                                                    surface_azimuth=tracker.surface_azimuth, 
                                                    solar_zenith=solpos.zenith, 
                                                    solar_azimuth=solpos.azimuth, 
                                                    dni=disc.dni, 
                                                    ghi=ghi, 
                                                    dhi=disc.dhi, 
                                                    dni_extra=etr_nrel, 
                                                    airmass=airmass.airmass_relative, 
                                                    albedo=irradiance.SURFACE_ALBEDOS[surface_type], 
                                                    surface_type=surface_type, 
                                                    model='perez', 
                                                    model_perez='allsitescomposite1990')

    return poa