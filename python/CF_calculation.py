# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 18:33:06 2024

@author: zhouj8
"""

import numpy as np
import ascrastergrid as ascgrid
import dir_accuflux as dirflux


def dir_accuflux(ldd, fr_riv, Tao, nodata_value):
    # set the boundary of map
    row_range = len(ldd)
    col_range = len(ldd[0])
    # set blanc map of FF_i
    FF_i = np.zeros_like(fr_riv)
    # loop for every cell: (I_0 = row, J_0 = row) is the cell coordination for filling in;(I_t, J_t) is the next cell coordination in downstream.
    # i is the source cell and j is receptor, they aren't represent coordination.

    for row in range(len(ldd)):
        for column in range(len(ldd[0])):
            #get flow direction ldd and the data for caculation fr_test
            icell_ldd = ascgrid.get_icell(ldd,row,column)
            icell_fr_riv = ascgrid.get_icell(fr_riv,row,column)
            if icell_ldd == nodata_value or icell_fr_riv == nodata_value:
                #nodata value
                continue
            elif icell_ldd < 0:
                print ("Negative mass flow of " + str(icell_ldd) + " at cell:( " + str(row) + "," +str(column) + ")")           
                # to next cell.
                continue
            elif icell_fr_riv < 0:
                print ("Negative fr_riv value of " + str(icell_fr_riv) + " at cell:( " + str(row) + "," +str(column) + ")")           
                # to exclude Go to next cell.
                continue
            elif icell_fr_riv == 0:
                icell_Tao_j = ascgrid.get_icell(Tao,row,column)
                FF_i[row][column] = icell_Tao_j  # If advection =0 meaning that advection doesn't flow to the downstreams, FFi_year = frii*taoi where frii =1
                continue
            else:
                # Normal cells which has value and flow direction information.
                I_0 = row
                J_0 = column
                I_t = I_0
                J_t = J_0
                # time
                t = 0
                # whether the flow ends in a rivermouth
                end_of_path = False
                # set the direction pointer
                direction = icell_ldd
                # define icell_FF_i
                icell_FF_i = 0
                # initiate fr_riv_ij(from cell i to j)= multiply until (j-1)
                icell_fr_ij = 1
                # FFii_year = frii*taoi where frii =1
                icell_Tao_j = ascgrid.get_icell(Tao,row,column)
                if icell_Tao_j <= 0:
                    icell_FF_i = None
                else: 
                    icell_FF_i = icell_fr_ij*icell_Tao_j
                # print("source cell (i,j),icell_FF_i =", I_0,J_0,icell_FF_i)
                while not end_of_path and t< row_range*col_range:
                    # print("\033[1;34;43m\goes to while again\033[0m")
                    # print("direction =", direction)
                    
                    if (direction < 1):
                        # Nodata_value
                        icell_FF_i = nodata_value
                        #print "Something is wrong with the lddmap (< 1). No river mouth found for icell: ",icell, " with load: ", flux, " and direction: ",direction
                        # Go to next cell
                        end_of_path=True
#                    elif (direction == 5):
#                        # Mouth of river basin is found. Assume the cumulative FF_i is fr_riv_IJ * Tao_i
#                        icell_FF_i = 0
#                        # Go to next cell
#                        end_of_path=True
                    elif (direction > 9):
                        # Nodata_value
                        icell_FF_i = nodata_value
                        #print "Something is wrong with the lddmap (> 9). No river mouth found for icell: ",icell, " with load: ", flux, " and direction: ",direction
                        # Go to next cell
                        end_of_path=True
                    else:
                        # get the Fr_riv of next cell until j-1 
                        icell_fr_next = ascgrid.get_icell(fr_riv,I_t,J_t)
                        # print("icell_fr_next =", icell_fr_next)
                        # the coordinate of cell: when time flows the coordinate goes to the next downstream cell
                        I_t,J_t,end_of_path = dirflux.goto_nextcell(direction,row_range, col_range, I_t,J_t)
                        # if the flow meet the end, jump out the loop and calculate the FF for the next source cell.
                        if end_of_path == True:
                            continue
                        # if the advection flow to the next downstream cell, aggregate FFij
                        else:
                            # get the direction, and N persistence of next (j) cell 
                            direction = ascgrid.get_icell(ldd,I_t,J_t)
                            icell_Tao_j = ascgrid.get_icell(Tao,I_t,J_t)
    #                        print("I,J,t, end of path",I_0,J_0,t,end_of_path)
    #                        print("I_t,I_t", I_t,J_t)
                            
                            # where the next cell's residence time is 0 or nodata_value,FF_i = 0
                            """ change Tao_j * EF if they are 0"""
                            if icell_fr_next <= 0:                            
                                end_of_path=True
                            elif icell_Tao_j <= 0:
                                # print("icell_Tao_j =", icell_Tao_j)
                                if direction == 5:
                                    break
                                # end_of_path=True
                                else:
                                    icell_fr_ij = icell_fr_ij * icell_fr_next
                                    continue
                                    # print("the code does not continue")

                            # where the next
                            
                            else:       
                                # Avoid errors of exceeding boundary
                                if I_t < row_range and I_t >= 0 and J_t < col_range and J_t >= 0:
                                    # Cumulatively multiply the neighbor Fr_riv to derive Fr_ij (from cell i to receptor j) 
                                    icell_fr_ij = icell_fr_ij * icell_fr_next
                                    icell_fr_riv = icell_fr_ij
                                    # Calculate the individual FF_ij(from cell i to receptor j)
                                    icell_FF_ij = icell_fr_ij * icell_Tao_j
                                    # print("icell_Tao_j =", icell_Tao_j)
                                    # print("icell_fr_riv =", icell_fr_riv)
                                    # Sum up the individual FF_ij to derive the cumulative FF_i (from cell i)
                                    
                                    if icell_FF_i is None:
                                        icell_FF_i = icell_FF_ij
                                    else:
                                        icell_FF_i += icell_FF_ij
                                    
                                    # icell_FF_i += icell_FF_ij
                                    # print("icell_FF_i =",icell_FF_i)
                                else:
                                    end_of_path=True
                                # # Mouth of river basin is found. Stop calculate
                                if direction == 5:
                                    end_of_path=True
                            # print("\033[1;31;40m\the code only continues going out if\033[0m")
                
                    # time steps adds
                    t = t + 1
                    
                #set data
                if icell_FF_i is None:
                    FF_i[I_0][J_0] = nodata_value
                else:
                    FF_i[I_0][J_0] = icell_FF_i
#            print("I,J,t, end of path",I_0,J_0,t,end_of_path)
#    print("fr_riv",fr_riv)
#    print("FF_i", FF_i)
    #set nodata_value
    '''
    '''
#    print("fr_riv",fr_riv)
    FF_i = np.where(FF_i < 0, nodata_value, FF_i)
    FF_i = np.where(ldd==nodata_value, ldd, FF_i)

    return FF_i

def CF_calculation(ldd, k_adv,k_all,ef_dvvolume):
    # To calculate fate factorsum of removal rates
    
    ########################### Calculate Nitrogen residence time T
    T_j = np.where(k_all < 0, -9999, 1/ k_all)
    T_j[np.isinf(T_j)] = 0
    T_j[np.isnan(T_j)] = 0

    ########################### multiply with EF*GEP for the receptors j
    TEG_j = np.where(T_j < 0,-9999,np.multiply(T_j,ef_dvvolume))
    TEG_j[np.isinf(TEG_j)] = -9999  
    TEG_j[np.isnan(TEG_j)] = -9999
    # avoid no value affect
    # TEG_j = np.where(TEG_j < 0,0,TEG_j)
    ######## Calculate Frac_riv
    '''
    '''
#    Frac_riv_i = np.where(k_all < 0, -9999,np.divide(k_adv,k_all,out=np.zeros_like(k_adv), where=k_all!=0))
    
    Frac_riv_i = np.where(k_all < 0, -9999,np.divide(k_adv,k_all))
    
#    print("Frac_riv_i",Frac_riv_i)
    Frac_riv_i[np.isinf(Frac_riv_i)] = 0
    Frac_riv_i[np.isnan(Frac_riv_i)] = 0

    ########################### Calculate cumulative FF_i
    CF_i = dir_accuflux(ldd, Frac_riv_i, TEG_j, -9999)
    CF_i[np.where(k_all==-9999)]=-9999
#    CF_i = np.where(CF_i < 0, -9999,np.divide(CF_i,volume,out=np.zeros_like(CF_i), where=volume!=0))
    CF_i[np.isinf(CF_i)] = -9999         
    CF_i[np.isnan(CF_i)] = -9999
    
    return CF_i
