import pvlib

def get_mount_tracker(with_tracker, surface_tilt, surface_azimuth, solpos, axis_tilt, axis_azimuth, max_angle, racking_model='open_rack', module_height=None):
    '''
    Docstring
    '''
    # Mount and Tracker
    if with_tracker == False:
        
        mount = pvlib.pvsystem.FixedMount(surface_tilt=surface_tilt, 
                                          surface_azimuth=surface_azimuth, 
                                          racking_model=racking_model, 
                                          module_height=module_height)
        tracker = None
        
    if with_tracker == True:
        mount = pvlib.pvsystem.SingleAxisTrackerMount(axis_tilt=axis_tilt, 
                                                      axis_azimuth=axis_azimuth, 
                                                      max_angle=max_angle, 
                                                      backtrack=True, 
                                                      gcr=0.2857142857142857, 
                                                      cross_axis_tilt=0.0, 
                                                      racking_model=racking_model, 
                                                      module_height=module_height) 
        
        tracker = mount.get_orientation(solar_zenith=solpos.apparent_zenith, 
                                        solar_azimuth=solpos.azimuth)
        
        tracker = tracker.fillna(0)
    
    return mount, tracker