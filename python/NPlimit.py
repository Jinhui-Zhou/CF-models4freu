# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 16:12:30 2022

@author: zhouj8
"""

"""
To make the N-P-limiting map by using Redfield Ratio
1: P-limited acceptable periphyton growth (type 1)
2: P-limited undesirable periphyton growth (type 2)
3: N-limited acceptable periphyton growth (type 3)
4: N-limited undesirable periphyton growth (type 4)
5: Simulated P and N concentration of zero (type 5)
6: Arid
"""
################# Parameters
import ascrastergrid as ascgrid
import residence_time as rt
# import map_plot as mplt
import numpy as np
import time
import math
import os
from os.path import dirname, abspath

# parameter
str_year = "2010"

# get root file
base_dir = dirname(dirname(dirname(abspath(__file__))))
base_dir = base_dir.replace('\\', '/')+"/"

directory_inscen = base_dir+"GNM_HOME/"
directory_root = base_dir

fileloc_inwater_y = "water_input/pcrglobwb_100/"+str_year+"/"
fileloc_inhist_y = "output_history_110/"+str_year+"/"
fileloc_inhistP_y = "output_history_110/P"+str_year+"/"
fileloc_inmap = "input/map_input/"+ str_year+"/"
filestr = "*.asc"


# start time
start = time.time()


#limiting map
def limiting_calculation(Nconc, Pconc, NPratio, discharge, nodata_value=-9999):
    # mask where 0 values
    mask_Nzero = (Nconc == 0) & (Pconc > 0) 
    mask_Pzero = (Pconc == 0) & (Nconc > 0)
    mask_allzero = (Pconc == 0) & (Nconc == 0)
    mask_arid = discharge == 0
    # set the boundary of map
    row_range = len(NPratio)
    col_range = len(NPratio[0])
    # set blanc map of NPlimit
    NPlimit = np.zeros_like(NPratio)
    # loop for every cell: row by row, column by column
    for row in range(row_range):
        for column in range(col_range):
            #get flow direction ldd and the data for caculation fr_test
            icell_NPratio = ascgrid.get_icell(NPratio,row,column)
            icell_Nconc = ascgrid.get_icell(Nconc,row,column)
            icell_Pconc = ascgrid.get_icell(Pconc,row,column)
            icell_NPlimit = 0
            if icell_NPratio == nodata_value or np.isinf(icell_NPratio) or np.isnan(icell_NPratio):
                #nodata value
                continue
            elif icell_NPratio < 7:
                # N limiting
                if icell_Nconc < 0.8:
                    icell_NPlimit = 3
                elif icell_Nconc >= 0.8:
                    icell_NPlimit = 4
                else:
                    print("Warning of N limit, NP ratio = " + str(icell_NPratio) + "Nconc = " +
                          str(icell_Nconc) + "Pconc = " + str(icell_Pconc) + 
                          " at cell:( " + str(row) + "," + str(column) + ")")
                    continue
            elif icell_NPratio >= 7:
                # P limiting
                if icell_Pconc < 0.046:
                    icell_NPlimit = 1
                elif icell_Pconc >= 0.046:
                    icell_NPlimit = 2
                else:
                    print("Warning of P limit, NP ratio = " + str(icell_NPratio) + "Nconc = " +
                          str(icell_Nconc) + "Pconc = " + str(icell_Pconc) + 
                          " at cell:( " + str(row) + "," + str(column) + ")")
                    continue

                #set data
            NPlimit[row][column] = icell_NPlimit
    #set nodata_value
    NPlimit[mask_Nzero] = 3
    NPlimit[mask_Pzero] = 1
    NPlimit[mask_allzero] = 5
    NPlimit[mask_arid] = 6
    
    NPlimit = np.where(NPlimit <= 0, -9999, NPlimit)

    return NPlimit

def main():
    ############## read N and P concentration ###############
    # read input files from GNM
    Nconc = ascgrid.read_ascii(directory_inscen,fileloc_inhist_y, "Nconc.asc")
    Pconc = ascgrid.read_ascii(directory_inscen,fileloc_inhistP_y, "Pconc.asc")
    discharge = ascgrid.read_ascii(directory_inscen,fileloc_inhistP_y, "discharge.asc")
    ############## revise the cell values for lakes ###############
    # id of lakes
    lakeid_grid = ascgrid.read_ascii(directory_inscen, fileloc_inwater_y, "waterbodyid.asc")
    # id of outlet of lakes
    outlakeid_grid = ascgrid.read_ascii(directory_inscen, fileloc_inwater_y, "waterbodyoutlet.asc")
    # set the lake values as lake outlet values
    Nconc_rt = rt.set_lake_rt(lakeid_grid, outlakeid_grid, Nconc)
    Pconc_rt = rt.set_lake_rt(lakeid_grid, outlakeid_grid, Pconc)
    ############## Calculate NPratio and the limiting map ###############
    mask_nonzero = (Pconc_rt > 0) & (Nconc_rt > 0)
    mask_novalue = (Nconc_rt == -9999) & (Pconc_rt == -9999)
    
    NPratio = np.zeros_like(Nconc_rt)
    NPratio[mask_nonzero] = np.divide(Nconc_rt[mask_nonzero],Pconc_rt[mask_nonzero])
    NPratio[mask_novalue] = -9999

    NPlimit = limiting_calculation(Nconc_rt, Pconc_rt, NPratio, discharge, nodata_value=-9999)
    #print(np.bincount(np.ndarray.flatten(NPlimit.astype(np.int64))))
    ascgrid.write_ascii_file(NPlimit, directory_root,fileloc_inmap,"NPlimit.asc")

if __name__ == "__main__":
    main()
# end time
end = time.time()
print("time used" + str(end-start))