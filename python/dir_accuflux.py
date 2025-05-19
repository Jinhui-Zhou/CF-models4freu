# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 18:23:04 2020

@author: zhouj8
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 15:31:50 2020

@author: zhouj8
"""


#generate random flowdirection, where 0 is nodata_value
import numpy as np
import ascrastergrid as ascgrid


def goto_nextcell(direction,row_range, col_range,ind_row, ind_col):
    '''
        Lddmap: network of local drain directions
    flow_direction can be coded as follows:
    UNH/GRDC                       PCraster(LDD)
    32 64 128   meaning: NW N NE       7 8 9
    16  -   1             W -  E       4 5 6
     8  4   2            SW S SE       1 2 3
    We use the PCraster LDD-format; negative and zero values are assumed
    '''
    ind_row_0,ind_col_0 = ind_row, ind_col
    try:
        if direction in [1,2,3]:
            ind_row += 1
            if direction == 1:
                ind_col -=1
            elif direction == 3:
                ind_col += 1
        elif direction in [4,5,6]:
            if direction == 4:
                ind_col -=1
            elif direction == 6:
                ind_col += 1
        elif direction in [7,8,9]:
            ind_row -= 1
            if direction == 7:
                ind_col -=1
            elif direction == 9:
                ind_col += 1
        else:
            raise Exception
            
        if ind_row < row_range and ind_row >= 0 and ind_col < col_range and ind_col >= 0:
            end_of_path = False
            return ind_row, ind_col,end_of_path
        else:
            end_of_path = True
            return ind_row_0,ind_col_0,end_of_path
        
    except:
        print("Goto_nextcell happens unknown errors.")
       
