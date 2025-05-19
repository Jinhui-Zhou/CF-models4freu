# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 14:48:11 2020

@author: zhouj8
"""

"""
To generate the map of freshwater CF (PDF·year·kgN-1)
'Export fraction from soil (FE_soil)', 'FE to rivers(FE_riv)' and 'Nitrogen Residence time in the receiving cell (tao_end)'

"""
################# Parameters

import residence_time as rt
import ascrastergrid as ascgrid
import dir_accuflux as dirflux
import dominant_process as dompc
import CF_calculation as CFcal
# import map_plot as mplt
import numpy as np
import time
import math
import os
from os.path import dirname, abspath
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Patch
import seaborn as sns
import sys



''' *********parameter to set before running the code*********'''
str_year = "2010"
''' directory--- open lines 37-39 and 69-70 for Nitrogen '''
fileloc_inhist_y = "output_history_110/"+str_year+"/"
fileloc_input_ef = "input/EF/"+ str_year+"/N/"
fileloc_result = "output/"+ str_year+"/N/"

'''  directory--- open lines 42-45 and 73-74 forPhosphorus '''
# fileloc_inhist_y = "output_history_110/P"+str_year+"/"
# fileloc_input_ef = "input/EF/"+ str_year+"/P/"
# fileloc_result = "output/"+ str_year+"/P/"

##################################################################
# get root file
base_dir = dirname(dirname(dirname(abspath(__file__))))
base_dir = base_dir.replace('\\', '/')+"/"

directory_inscen = base_dir+"GNM_HOME/"
directory_root = base_dir
fileloc_inwater = "water_input/pcrglobwb_100/"
fileloc_input_wu = "input/water_use_input/"
#fileloc_inhist = "output_history_110/"
fileloc_input_map = "input/map_input"

fileloc_inwater_y = "water_input/pcrglobwb_100/"+str_year+"/"
fileloc_input_wu_y = "input/water_use_input/"+str_year+"/"

filestr = "*.asc"

# start time
# sys.stdout = open(directory_root+fileloc_result+"console_log.txt", 'w')
start = time.time()

############## read EF ###############
''' directory--- open lines 69-70 for Nitrogen '''
average_EFGEP = ascgrid.unify_coordinate_fromfile(directory_root,fileloc_input_ef, "average_efgep.asc")
marginal_EFGEP = ascgrid.unify_coordinate_fromfile(directory_root,fileloc_input_ef, "marginal_efgep.asc")

''' directory--- open lines 73-74 for Phosphorus '''
# average_EFGEP = ascgrid.unify_coordinate_fromfile(directory_root,fileloc_input_ef, "average_efgep_P.asc")
# marginal_EFGEP = ascgrid.unify_coordinate_fromfile(directory_root,fileloc_input_ef, "marginal_efgep_P.asc")

############## Calculate FF ###############
# read input files from GNM
    # normalize by freshwater volume
volumefw_grid = ascgrid.read_ascii(directory_inscen, fileloc_inwater_y, "wst.asc")
average_EFGEP_dv = np.where(average_EFGEP < 0, -9999,np.divide(average_EFGEP,volumefw_grid,out=np.zeros_like(average_EFGEP), where=volumefw_grid!=0))
marginal_EFGEP_dv = np.where(marginal_EFGEP < 0, -9999,np.divide(marginal_EFGEP,volumefw_grid,out=np.zeros_like(marginal_EFGEP), where=volumefw_grid!=0))
    # cellarea
data_cellarea = ascgrid.read_ascii(directory_inscen, fileloc_inwater, "cellarea30.asc")
    #fraction of water area in a cell
data_fracwat = ascgrid.read_ascii(directory_inscen, fileloc_inwater_y, "fracwat.asc")
data_residence_time = ascgrid.read_ascii(directory_inscen, fileloc_inhist_y, "residence_time.asc")
data_retention = ascgrid.read_ascii(directory_inscen, fileloc_inhist_y, "retention.asc")
data_discharge = ascgrid.read_ascii(directory_inscen, fileloc_inhist_y, "discharge.asc")
# id of lakes
lakeid_grid = ascgrid.read_ascii(directory_inscen, fileloc_inwater_y, "waterbodyid.asc")
# id of outlet of lakes
outlakeid_grid = ascgrid.read_ascii(directory_inscen, fileloc_inwater_y, "waterbodyoutlet.asc")
# exclude greenland map
greenland = ascgrid.unify_coordinate_fromfile(directory_root,fileloc_input_map, "greenland1.asc")

########Calculate the whole water consumption
""" 
agricultural water use (data_agwu) is in the unit of m3 yr-1    
discharge is in km3 yr-1
fr_u_agr is the array of f(u,agr,i) = data_agwu/discharge* 10^-9
"""
#read the total agricultural water use form water input file
data_agwu = ascgrid.read_ascii(directory_root, fileloc_input_wu_y, "AGWU_05.asc")


# Calculate the fraction of agricultural water use
  # discharge larger than 6 mm in non-arid zone
fr_u_agr = np.where(data_discharge < 3025*6*10**(-6),-9999,np.divide(data_agwu*10**(-9),data_discharge,out=np.zeros_like(data_agwu), where=data_discharge!=0))
fr_u_agr[np.isinf(fr_u_agr)] = -9999  
fr_u_agr[np.isnan(fr_u_agr)] = -9999
fr_u_agr = np.where(data_discharge == -9999, data_discharge,fr_u_agr)
"""
Domestic and industrial water use includes Dom, Elec, Live, and Man consumption, in the unit of kg m-2 s-1
fr_con_indst is the array of f_con,dom,i+f_{con,elc,i}+f_{con,man,i}+f_{con,lvs,i}
fr_con_indst = data_indstcon/discharge *10-3*365*86400
"""
#read the total domestic and industrial water use form water input file
data_domcon_perarea = ascgrid.read_ascii(directory_root, fileloc_input_wu_y, "watergap_DomCon"+str_year+".asc")
data_eleccon_perarea = ascgrid.read_ascii(directory_root, fileloc_input_wu_y, "watergap_ElecCon"+str_year+".asc")
data_livecon_perarea = ascgrid.read_ascii(directory_root, fileloc_input_wu_y, "watergap_LiveCon"+str_year+".asc")
data_mancon_perarea = ascgrid.read_ascii(directory_root, fileloc_input_wu_y, "watergap_ManCon"+str_year+".asc")
data_landarea = ascgrid.read_ascii(directory_root, fileloc_input_wu, "landarea.asc")

#Calculate domestic and industrial water consumption
data_indstcon_perarea = data_domcon_perarea + data_eleccon_perarea + data_livecon_perarea + data_mancon_perarea
data_indstcon_perarea = np.where(data_indstcon_perarea >= 1.000000020040877343e+20, 0,data_indstcon_perarea)
data_indstcon = np.multiply(data_indstcon_perarea,data_landarea)
data_indstcon = np.where(data_indstcon <= 0, 0.,data_indstcon)


# Calculate fraction of domestic and industrial water consumption
   ### if ignore discharge under 6 mm in non-arid zone
fr_con_indst = np.where(data_discharge < 3025*6*10**(-6), -9999,np.divide(data_indstcon*365*86.4*10**(-3),data_discharge,out=np.zeros_like(data_indstcon), where=data_discharge!=0))
fr_con_indst[np.isinf(fr_con_indst)] = -9999         
fr_con_indst[np.isnan(fr_con_indst)] = -9999
fr_con_indst = np.where(data_discharge == -9999, data_discharge,fr_con_indst)
####### mask by aridity index
aridity = ascgrid.unify_coordinate_fromfile(directory_root, fileloc_input_wu, "ai_05.asc")
aridity[np.where((aridity < 2000) & (data_discharge < 3025*325*10**(-6)))] = -9999
fr_u_agr = np.where(aridity == -9999, aridity, fr_u_agr)
fr_con_indst = np.where(aridity == -9999, aridity, fr_con_indst)

'''
Calculate removal rate of advection, retention and wateruse. unit is yr-1
'''
fr_water_use = np.where(fr_con_indst == -9999, -9999, fr_u_agr + fr_con_indst)
## set fraction of water use where the discharge is tiny as nodata
fr_water_use = np.where(fr_u_agr == -9999, fr_u_agr, fr_water_use)

        
'''set residence time for lakes from PCR-GLOBWB'''
residencetime = rt.set_lake_rt(lakeid_grid, outlakeid_grid, data_residence_time)

    # advextion removal rates 
k_adv = np.where(data_residence_time < 0,-9999, 1/np.array(residencetime))
k_adv[np.isinf(k_adv)] = 0
k_adv[np.isnan(k_adv)] = 0

    # retention rates
'''set retention for lakes from PCR-GLOBWB'''
data_retention = rt.set_lake_rt(lakeid_grid, outlakeid_grid, data_retention)
data_retention[np.where(data_retention == 1)] = 0.999999
log1_ret = np.where(data_retention ==-9999, -9999,-np.log(1-data_retention))
k_ret = np.where(data_retention ==-9999, -9999,k_adv*log1_ret)
k_ret[np.isinf(k_ret)] = 0
k_ret[np.isnan(k_ret)] = 0

    # water use removal rates
k_wuse = np.where(fr_water_use <0, -9999,np.multiply(fr_water_use,k_adv))
k_wuse[np.isinf(k_wuse)] = 0
k_wuse[np.isnan(k_wuse)] = 0

# sum of removal rates
k_all = np.where(fr_water_use <0, -9999, k_adv + k_ret + k_wuse)
k_all[greenland>=0]=-9999
# mask the map
# k_all_marginal = np.where(marginal_EFGEP < 0, -9999,k_all)
# k_all_average = np.where(average_EFGEP < 0, -9999,k_all)

########################### Calculate cumulative CF_i ########################### 
## read ldd map
ldd = ascgrid.read_ascii(directory_inscen, fileloc_inwater, "ldd.map")
### Choose whether to calculate FF_i sollely or to calculate both FF_i and dominant process
print("Calculation of CF marginal.")
CF_i_marginal = CFcal.CF_calculation(ldd, k_adv,k_all,marginal_EFGEP_dv)   ## Calculate FF_i solely ---choice1

print("Calculation of CF average.")
CF_i_average = CFcal.CF_calculation(ldd, k_adv,k_all,average_EFGEP_dv)   ## Calculate FF_i solely ---choice1

#CF_i_average,x_all,x_adv,x_ret,x_wuse = dompc.dominant_calculation(ldd, k_adv,k_ret,k_wuse,k_all_average,average_EFGEP)   ## Calculate FF_i and dominant process ----choice2
#CF_i_marginal,x_all,x_adv,x_ret,x_wuse = dompc.dominant_calculation(ldd, k_adv,k_ret,k_wuse,k_all_marginal,marginal_EFGEP)   ## Calculate FF_i and dominant process ----choice2


############################ write asc files 
ascgrid.write_ascii_file(CF_i_marginal, directory_root,fileloc_result,"CF_marginal_freshwater.asc")
ascgrid.write_ascii_file(CF_i_average, directory_root,fileloc_result,"CF_average_freshwater.asc")


# end time
end = time.time()
print(end-start)
# sys.stdout.close()

