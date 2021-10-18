import pvlib

def get_parameters(latitude, longitude, tz, altitude, datetime):
    # Geographic Location
    location = pvlib.location.Location(latitude, longitude, tz, altitude)
    
    # Solar Position Parameters
    solpos = location.get_solarposition(times=datetime, 
                                        method='nrel_numpy')

    # Airmass
    airmass = location.get_airmass(times=datetime, 
                                   solar_position=solpos, 
                                   model='kastenyoung1989')

    # Extraterrestrial DNI
    etr_nrel = pvlib.irradiance.get_extra_radiation(datetime_or_doy=datetime, 
                                                    method='NREL', 
                                                    solar_constant=1361)

    return location, solpos, airmass, etr_nrel