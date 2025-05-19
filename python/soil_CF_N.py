# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 16:42:54 2020

@author: zhouj8
"""
"""
To generate the map of diffusive emission CF (PDF.year.kgN-1) and erosion CF (PDF.year/(m2.year))

"""

import ascrastergrid as ascgrid
import re
import os
from os.path import dirname, abspath
import numpy as np 
#
#string = '394*0.00000 219.343 3*0.00000 219.343 0.00000 219.343 319*0.00000'
#

# parameter
str_year = "2010"

# get root file
base_dir_gmff = dirname(dirname(dirname(abspath(__file__))))
base_dir_gmff = base_dir_gmff.replace('\\', '/')+"/"


# GNMinput file path
directory_root = base_dir_gmff+"input/GNM_input/"
GNMinput_path = directory_root+ str_year+"/N/"
direcotry_out = base_dir_gmff+"output/"+str_year+"/N/"

print (GNMinput_path)
# input filename

filepath_Nbal_arable = GNMinput_path + "balance_N-NH3_arable.asc"
filepath_Nbal_grs = GNMinput_path + "balance_N-NH3_grs.asc"
filepath_Nbal_nat = GNMinput_path + "balance_N-NH3_nat.asc"



def arr_divide(numerater_array, denominator_array,nodata_val = -9999):
    fr = np.where(denominator_array == 0, 0, np.divide(numerater_array,denominator_array))
    fr[np.where(numerater_array < 0)] = nodata_val
    fr[np.where(denominator_array < 0)] = nodata_val
    fr[np.isinf(fr)] = nodata_val         
    fr[np.isnan(fr)] = nodata_val
    return fr

def arr_multiply(arr_1, arr_2, nodata_val = -9999):
    out_arr = np.where(arr_1 < 0, nodata_val, np.multiply(arr_1,arr_2))
    out_arr[np.where(arr_2 < 0)] = nodata_val
    out_arr[np.isinf(out_arr)] = nodata_val         
    out_arr[np.isnan(out_arr)] = nodata_val
    return out_arr


'''Soil FF --- diffusive emissions'''
## read files
##option1 ----2000
#N_emission_tot = ascgrid.read_ascii(GNMinput_path, "emission/", "N_emission_lu.asc")
##option2 ----other years
N_emission_grs = ascgrid.read_ascii(GNMinput_path, "emission/", "balance_N-NH3_grs.asc")
N_emission_nat = ascgrid.read_ascii(GNMinput_path, "emission/", "balance_N-NH3_nat.asc")
N_emission_ara = ascgrid.read_ascii(GNMinput_path, "emission/", "balance_N-NH3_arable.asc")

N_emission_tot = N_emission_grs + N_emission_nat + N_emission_ara
ascgrid.write_ascii_file(N_emission_tot,GNMinput_path, "emission/", "N_emission_diffuse.asc")
# FF_freshwater
CF_i_marginal = ascgrid.read_ascii(direcotry_out,"","CF_marginal_freshwater.asc")
CF_i_average = ascgrid.read_ascii(direcotry_out,"","CF_average_freshwater.asc")


## diffusion
N_sro = ascgrid.read_ascii(GNMinput_path, "output/", "N_sro.asc")

## diffusion   
N_diffuse = N_sro.copy()   # diffusion without npp

# fraction of emission transported by runoff, drainage and groundwater leaching as a result of fertilizer .etc application
fr_soil_dr = arr_divide(N_diffuse,N_emission_tot)

CF_soil_marginal_dr = arr_multiply(fr_soil_dr, CF_i_marginal)
CF_soil_average_dr = arr_multiply(fr_soil_dr, CF_i_average)


# FF_soil year * kgN/ kg
ascgrid.write_ascii_file(CF_soil_marginal_dr,direcotry_out, "", "CF_marginal_diffuse.asc")
ascgrid.write_ascii_file(CF_soil_average_dr,direcotry_out, "", "CF_average_diffuse.asc")

### FF- erosion  year * kg N/(km2*year)
# N loss from soil (kg N/year)
Nsoilloss_arable = ascgrid.read_ascii(GNMinput_path, "output/", "Nsoilloss_arable.asc")
Nsoilloss_grass = ascgrid.read_ascii(GNMinput_path, "output/", "Nsoilloss_grass.asc")
Nsoilloss_nat = ascgrid.read_ascii(GNMinput_path, "output/", "Nsoilloss_nat.asc")

# landuse area (km2)
area_crop = ascgrid.read_ascii(directory_root, str_year+"/", "area_crop.asc")
area_grass = ascgrid.read_ascii(directory_root, str_year+"/", "area_grass.asc")
area_nat = ascgrid.read_ascii(directory_root, str_year+"/", "area_nat.asc")

area_crop[np.where((area_crop < 0.000001) & (area_crop >= 0))] = 0  # remove small area
area_grass[np.where((area_grass < 0.000001) & (area_grass >= 0))] = 0   # remove small area
area_nat[np.where((area_nat < 0.000001) & (area_nat >= 0))] = 0   # remove small area

# fraction of soil loss (erosion)  kg N/(km2*year)
fr_soil_erosion_arable = arr_divide(Nsoilloss_arable,area_crop)
fr_soil_erosion_grass = arr_divide(Nsoilloss_grass,area_grass)
fr_soil_erosion_nat = arr_divide(Nsoilloss_nat,area_nat) 
##fraction of erosion based on natural land 
#fr_soil_erosion_base = np.where(fr_soil_erosion_nat < 0, fr_soil_erosion_grass/(2.413793802+1),fr_soil_erosion_nat)  # merge grasland value when natural land area is 0
#fr_soil_erosion_base = np.where(fr_soil_erosion_base < 0, fr_soil_erosion_arable/(45.3046739+1),fr_soil_erosion_base) # merge arable land
#fr_soil_erosion_base[np.where(fr_soil_erosion_base < 0)] = -9999
# CF erosion-natural land subtraction as the base
#CFimgn_soil_erosion_base = arr_multiply(fr_soil_erosion_base,10**(-6)*CF_i_marginal)


CF_marginal_erosion_nat = arr_multiply(fr_soil_erosion_nat,10**(-6)*CF_i_marginal) # CF_marginal-erosion natural land 
CF_marginal_erosion_grass = arr_multiply(fr_soil_erosion_grass,10**(-6)*CF_i_marginal) # CF_marginal-erosion grassland
CF_marginal_erosion_arable = arr_multiply(fr_soil_erosion_arable,10**(-6)*CF_i_marginal) # CF_marginal-erosion arable land

CF_average_erosion_nat = arr_multiply(fr_soil_erosion_nat,10**(-6)*CF_i_average) # CF_marginal-erosion natural land 
CF_average_erosion_grass = arr_multiply(fr_soil_erosion_grass,10**(-6)*CF_i_average) # CF_marginal-erosion grassland
CF_average_erosion_arable = arr_multiply(fr_soil_erosion_arable,10**(-6)*CF_i_average) # CF_marginal-erosion arable land

# subtraction of CF for pasture and arable land
CFsub_marginal_erosion_grass = np.where(CF_marginal_erosion_grass < 0, -9999, CF_marginal_erosion_grass-CF_marginal_erosion_nat)
CFsub_marginal_erosion_grass[np.where(CFsub_marginal_erosion_grass < 0)] = -9999
#CFsub_marginal_erosion_grass[np.where(CF_marginal_erosion_nat < 0)] = -9999

CFsub_marginal_erosion_arable = np.where(CF_marginal_erosion_arable < 0, -9999, CF_marginal_erosion_arable-CF_marginal_erosion_nat)
CFsub_marginal_erosion_arable[np.where(CFsub_marginal_erosion_arable < 0)] = -9999
#CFsub_marginal_erosion_arable[np.where(CF_marginal_erosion_nat < 0)] = -9999

CFsub_average_erosion_grass = np.where(CF_average_erosion_grass < 0, -9999, CF_average_erosion_grass-CF_average_erosion_nat)
CFsub_average_erosion_grass[np.where(CFsub_average_erosion_grass < 0)] = -9999
#CFsub_average_erosion_grass[np.where(CF_average_erosion_nat < 0)] = -9999

CFsub_average_erosion_arable = np.where(CF_average_erosion_arable < 0, -9999, CF_average_erosion_arable-CF_average_erosion_nat)
CFsub_average_erosion_arable[np.where(CFsub_average_erosion_arable < 0)] = -9999
#CFsub_average_erosion_arable[np.where(CF_average_erosion_nat < 0)] = -9999


# write files of erosion
#ascgrid.write_ascii_file(fr_soil_erosion_base,direcotry_out, "CF_soil/", "fr_soil_erosion_base.asc")
#ascgrid.write_ascii_file(fr_soil_erosion_arable,direcotry_out, "CF_soil/", "fr_soil_erosion_arable.asc")
#ascgrid.write_ascii_file(fr_soil_erosion_grass,direcotry_out, "CF_soil/", "fr_soil_erosion_grass.asc")
#ascgrid.write_ascii_file(fr_soil_erosion_nat,direcotry_out, "CF_soil/", "fr_soil_erosion_nat.asc")
#ascgrid.write_ascii_file(CFimgn_soil_erosion_base,direcotry_out, "CF_soil/", "CFimarginal_soil_erosion_base.asc")
#ascgrid.write_ascii_file(CFiave_soil_erosion_base,direcotry_out, "CF_soil/", "CFiaverage_soil_erosion_base.asc")
#ascgrid.write_ascii_file(FF_soil_erosion_nat,direcotry_out, "GNM/FF_soil/", "FF_soil_erosion_nat.asc")
ascgrid.write_ascii_file(CFsub_marginal_erosion_grass,direcotry_out, "", "CF_marginal_erosion_grass.asc")
ascgrid.write_ascii_file(CFsub_marginal_erosion_arable,direcotry_out, "", "CF_marginal_erosion_arable.asc")
ascgrid.write_ascii_file(CFsub_average_erosion_grass,direcotry_out, "", "CF_average_erosion_grass.asc")
ascgrid.write_ascii_file(CFsub_average_erosion_arable,direcotry_out, "", "CF_average_erosion_arable.asc")

#ascgrid.write_ascii_file(fr_soil_dr,direcotry_out, "CF_soil/", "fr_soil_dr.asc")

