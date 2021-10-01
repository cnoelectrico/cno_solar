import pvlib

def get_mount_tracker(with_tracker, surface_tilt, surface_azimuth, solpos, axis_tilt, axis_azimuth, max_angle, tracker_axis, racking_model='open_rack', module_height=None):

    # Mount
    if with_tracker == False:
        mount = pvlib.pvsystem.FixedMount(surface_tilt=surface_tilt, 
                                          surface_azimuth=surface_azimuth, 
                                          racking_model=racking_model, 
                                          module_height=module_height)
    if with_tracker == True:
        mount = pvlib.pvsystem.SingleAxisTrackerMount(axis_tilt=axis_tilt, 
                                                      axis_azimuth=axis_azimuth, 
                                                      max_angle=max_angle, 
                                                      backtrack=True, 
                                                      gcr=0.2857142857142857, 
                                                      cross_axis_tilt=0.0, 
                                                      racking_model=racking_model, 
                                                      module_height=module_height)        

    # Tracker
    if with_tracker == False:
        tracker_axis = 0
        tracker = None
    
    if tracker_axis == 1:
        tracker = pvlib.tracking.singleaxis(apparent_zenith=solpos.apparent_zenith, 
                                            apparent_azimuth=solpos.azimuth, 
                                            axis_tilt=axis_tilt,
                                            axis_azimuth=axis_azimuth, #Heading south
                                            max_angle=max_angle, 
                                            backtrack=True, 
                                            gcr=0.2857142857142857)

        tracker = tracker.fillna(0) 
    
    return mount, tracker