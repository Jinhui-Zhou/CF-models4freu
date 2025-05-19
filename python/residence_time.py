# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 15:24:06 2020

@author: zhouj8
"""
import numpy as np
import ascrastergrid as ascgrid

'''method of Wollheim et al.2006'''
def depth_of_river(discharge):

    # extimation of depth of river D = ad* Q^bd. Q: discharge, km3/yr; D:depth, km. (Wollheim et al. 2006)
    depth = 1.04*10**(-3) * discharge**0.37
    depth[np.where(discharge==-9999)]=-9999

    return depth

def residence_time_adjust(data_residence_time, water_area, data_discharge):
    depth = depth_of_river(data_discharge)
    
    # water_volume = water_area*depth
    water_volume = np.where(water_area == -9999, -9999, np.multiply(water_area,depth))
    water_volume[np.where(depth==-9999)] = -9999

    
    # residencetime = water_volume/discharge, (yr); water volume (km3)
    residencetime = np.copy(data_residence_time)
    # avoiding discharge too low
    residencetime = np.where(data_residence_time != 0, data_residence_time, np.divide(water_volume,data_discharge,where=data_discharge !=0))
#    residencetime = np.where(data_residence_time != 0, data_residence_time, np.divide(water_volume,data_discharge))
    residencetime[np.where(data_discharge==-9999)] = -9999
    residencetime[np.where(water_volume==-9999)] = -9999
    residencetime[np.isinf(residencetime)] = -9999         
    residencetime[np.isnan(residencetime)] = -9999

    return residencetime

'''set residence time for lakes'''
def set_lake_rt(lakeid_grid, outlakeid_grid, data_residence_time):
    # Correct residence time when there is a reservoir or a lake.
        # set the boundary of map
    row_range = len(data_residence_time)
    col_range = len(data_residence_time[0])
    # set blanc map of data_residence_time
    rt = np.copy(data_residence_time)
    # loop for every cell
    for row in range(row_range):
        for column in range(col_range):
            icell_outid = ascgrid.get_icell(outlakeid_grid,row,column)
            if (icell_outid > 0):
               # Check whether it is a outlet of a lake or reservoir
               icell_rt = ascgrid.get_icell(data_residence_time,row,column)
               # set the residence time of outlake to the whole lake
               rt[np.where(lakeid_grid ==icell_outid)] = icell_rt
    return rt
