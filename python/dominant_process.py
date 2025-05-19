# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 23:28:06 2020

@author: zhouj8
"""

import numpy as np
import ascrastergrid as ascgrid
import CF_calculation as CFcal

                       
def comparison_data_max(data1,data2,data3):
    ## *This function is to calculate the max removal process and provide its map.
    try:
        #to find whether the shape of data are compatible/if not,go to exception
        
        if np.shape(data1) == np.shape(data2) ==np.shape(data3):
            #create a array
            array_index_max = np.zeros_like(data1)
            row_range = len(data1)
            col_range = len(data1[0])
            # loop for every cell: 
            for row in range(row_range):
                for column in range(col_range):
                    icell1 = ascgrid.get_icell(data1,row,column) # advection
                    icell2 = ascgrid.get_icell(data2,row,column) # retention
                    icell3 = ascgrid.get_icell(data3,row,column) # water consumption
                    if icell1 ==-9999 or icell2 ==-9999 or icell3 == -9999:
                        array_index_max[row,column] = -9999
                    elif icell1 == 0 and icell2 == 0 and icell3 == 0:
                        array_index_max[row,column] = 0
                    elif icell1 == max([icell1, icell2,icell3]):
                        array_index_max[row,column] = 1
                    elif icell2 == max([icell1, icell2,icell3]):
                        array_index_max[row,column] = 2
                    elif icell3 == max([icell1, icell2,icell3]):
                        array_index_max[row,column] = 3
                    else:
                        continue
            return array_index_max
        else:
            raise Exception("The data are not compatible: Max determination.")
    except:
        raise Exception("The data are not compatible: Max determination.")                        

def dominant_calculation(ldd, k_adv,k_ret,k_wuse,k_all,ef,directory_root = "C:/Users/zhouj8/Desktop/zhouj/01Research/02FF_N_GNM/02model/gmFF2000/",fileloc_result = "output_history/map2000/"):
    # not consider retention removal
    k_noret = np.where(k_wuse < 0, -9999, k_adv + k_wuse)
    # not consider water use removal
    k_nowuse = np.where(k_wuse < 0, -9999, k_adv + k_ret)
    # Calculate FFi which includes all removal rate
    CF_all = CFcal.CF_calculation(ldd, k_adv,k_all,ef)
    # Calculate FFi which includes only advection and water use, exclude retention
    CF_noret = CFcal.CF_calculation(ldd, k_adv,k_noret,ef)
    # Calculate FFi which includes only advection and retention, exclude water use
    CF_nowuse = CFcal.CF_calculation(ldd, k_adv,k_nowuse,ef)
    # Calculate FFi which includes only advection
    CF_adv = CFcal.CF_calculation(ldd, k_adv,k_adv,ef)
    
    # Net removal rate of all removal process
    x_all = np.where(CF_all == -9999,-9999,np.divide(1,CF_all))
    x_all[np.isinf(x_all)] = -9999  
    x_all[np.isnan(x_all)] = -9999
    
    # importance of advection
    x_adv = np.where(CF_adv == -9999,-9999,np.divide(1,CF_adv))
    x_adv[np.isinf(x_adv)] = -9999  
    x_adv[np.isnan(x_adv)] = -9999
     
    # importance of retention removal
    x_ret = np.where(CF_all == -9999,-9999,np.divide(1,CF_all)-np.divide(1,CF_noret))
    x_ret[np.isinf(x_ret)] = -9999  
    x_ret[np.isnan(x_ret)] = -9999
    # importance of water use removal
    x_wuse = np.where(CF_all == -9999,-9999,np.divide(1,CF_all)-np.divide(1,CF_nowuse))
    x_wuse[np.isinf(x_wuse)] = -9999  
    x_wuse[np.isnan(x_wuse)] = -9999
    
    ascgrid.write_ascii_file(x_adv, directory_root,fileloc_result,"GNM/Net_removal_rate_adv.asc")
    ascgrid.write_ascii_file(x_ret, directory_root,fileloc_result,"GNM/Net_removal_rate_ret.asc")
    ascgrid.write_ascii_file(x_wuse, directory_root,fileloc_result,"GNM/Net_removal_rate_wuse.asc")
    ascgrid.write_ascii_file(x_all, directory_root,fileloc_result,"GNM/Net_removal_rate_all.asc")
    
    return CF_all,x_all, x_adv,x_ret,x_wuse
        
def Net_removal_contrbution(x_remove,x_all,contribution_index=0.1):
    # This function calculate the contribution (%) of water consumption
    try:
        #to find whether the shape of data are compatible/if not,go to exception
        
        if np.shape(x_remove) == np.shape(x_all):
            #create a array
            array_index = np.zeros_like(x_remove)
            row_range = len(x_remove)
            col_range = len(x_remove[0])
            # loop for every cell: 
            for row in range(row_range):
                for column in range(col_range):
                    icell1 = ascgrid.get_icell(x_remove,row,column)
                    icell2 = ascgrid.get_icell(x_all,row,column)
                    if icell1 ==-9999 or icell2 ==-9999:
                        array_index[row,column] = -9999
                    elif icell1 == 0 and icell2 == 0:
                        array_index[row,column] = 0
                    elif icell1 >= contribution_index*icell2:
                        array_index[row,column] = 1
                    elif icell1 < contribution_index*icell2:
                        array_index[row,column] = 2
                    else:
                        continue
            contribution = np.sum(array_index==1)/np.sum(array_index>=1)
            print ("Net removal: Water consumption contributing {a:.2f} of total net removal rates occupies {b:.4f} of cells.".format(a=contribution_index,b=contribution))
            return contribution
        else:
            raise Exception("The data are not compatible: contribution of net removal rate.")
    except:
        raise Exception("The process are interupted due to error: contribution of net removal rate.")                

def Net_removal_contrbt_map(x_remove,x_all,name="advection"):    
    # This function provides a map of contribution for the removal process
    try:
    #to find whether the shape of data are compatible/if not,go to exception
        if np.shape(x_remove) == np.shape(x_all):
            #create a array
            arr_contribution = np.zeros_like(x_remove)
            row_range = len(x_remove)
            col_range = len(x_remove[0])
            # loop for every cell: 
            for row in range(row_range):
                for column in range(col_range):
                    icell1 = ascgrid.get_icell(x_remove,row,column)
                    icell2 = ascgrid.get_icell(x_all,row,column)
                    if icell1 ==-9999 or icell2 ==-9999:
                        arr_contribution[row,column] = -9999
                    elif icell1 == 0 and icell2 == 0:
                        arr_contribution[row,column] = -9999
                    elif icell2 !=0:
                        arr_contribution[row,column] = icell1/icell2
                    else:
                        continue
            print ("Net removal: {a} contribution map is sucessfully made.".format(a=name))
            return arr_contribution
        else:
            raise Exception("The data are not compatible: contribution of net removal rate.")
    except:
        raise Exception("The process are interupted due to error: contribution of net removal rate.")    