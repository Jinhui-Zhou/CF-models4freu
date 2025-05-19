# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 21:38:05 2020

@author: zhouj8
"""
import glob
import re
import numpy as np
import gzip
import os
import rasterio

class Error(Exception):
    """Base class for exceptions in this module."""
    pass
class ASCIIGridError(Error):
    '''Is raised when a ASCII grid file is not valid.
    
    file: file object of the ASCII grid
    message: message with explanation on failure
    '''
    def __init__(self, message, file = None):
        self.message = message
        if file != None:
            self.filename= file.name
            self.__hasfile = True
            # Close the opened file
            file.close()
        else:
            self.__hasfile = False
        
    def __str__(self):
        if self.__hasfile:
            return repr((self.filename, self.message))
        else:
            return repr(self.message)

#def read_ascii(directory, file_loc, filestr, skip):
#    filenames = glob.glob(directory + file_loc + filestr)
#    data =  np.loadtxt(filenames[0],skiprows=skip)
#    return data

def read_ascii(directory, file_loc, filestr):
    """read a raster file
    return the data in the form of array"""
    filename1 = os.path.join(directory, file_loc, filestr)
    with rasterio.open(filename1) as raster_infile:
        data = raster_infile.read(1)
    return data

def get_length(data):
    """get the legth of a numpy array/matrix/two-dimension list"""
    data_arr= np.array(data)
    ncols = len(data_arr[0])
    nrows = len(data_arr)
    length = ncols * nrows
    return length


def get_icell(data, ind_row, ind_col, val = None):
    '''
    Get data value for a given index position. When the index position is NoData None is returned.
    When val is not None, val will be returned in stead of None (in case of NoData) 
    Value returned as FLOAT or INTEGER.
    @param ind: Index for the asked value
    @type ind: INTEGER
    @param val: Default value in stead of None in case of Nodata
    @type val: FLOAT 
    '''
    # If the given index falls outside the given domain, raise ASCIIGridError
    length = get_length(data)
    
    if ind_col*ind_row >= length or ind_row < 0 or ind_col < 0: 
        raise ASCIIGridError("Index position %s falls outside bounds." % ind_row, ind_col)

    returnValue = data[ind_row][ind_col]
    return returnValue

#def set_data(data, ind_row, ind_col, value):
#        '''
#        Get data value for a given index position.
#        @param ind: Index for the asked value
#        @type ind: INTEGER
#        @param value: New value as float or integer
#        @type value: FLOAT/INTEGER
#        '''
#        length = get_length(data)
#        if ind_col*ind_row >= length or ind_row < 0 or ind_col < 0: 
#            raise ASCIIGridError("Index position %s falls outside bounds." % ind_row, ind_col)
#            values[ind_row][ind_col] = value
#        return values[ind_row][ind_col]
    
def write_ascii_file(data, directory,fileloc,filestr,ncols=720,nrows=360,xllcorner=-180,yllcorner=-90,cellsize=0.5,nodata_value = -9999):
    """ write data into ascii file
    return an asc file"""
    
    header_string  = 'ncols '+str(ncols)+'\n' \
                      +'nrows '+ str(nrows)+'\n' \
                      +'xllcorner '+str(xllcorner)+'\n' \
                      + 'yllcorner '+ str(yllcorner)+'\n' \
                      + 'cellsize '+ str(cellsize) +'\n' \
                      + 'NODATA_value '+ str(nodata_value)
    np.savetxt(directory + fileloc + filestr ,data, header=header_string, comments='')

def read_headers(directory, file_loc, filestr):
    '''Read the header information from a ASCIIgrid.
    Returns a dictionary with the header properties.'''
    hps = {'ncols':None,
           'nrows':None,
           'xllcorner':None,
           'yllcorner':None,
           'cellsize':None,
           'nodata_value':None}
    filenames = os.path.join(directory, file_loc, filestr)
    
    # Opening grid ascii file  
    try:
        if os.path.exists(filenames):
            f = open(filenames, 'r')
        else:
            raise Exception("Error in opening file: %s" % filenames)
    except IOError:
        raise Exception("Error in opening file: %s" % filenames)
    
    line = f.readline()
    #scan first 6 lines for parameters
    for _i in range(6):
        line_info = line.replace('\n', '').split()
        # Check if the found key is a valid keyword
        if hps.__contains__(line_info[0].lower()):
            # set the value to the dictionary
            hps[line_info[0].lower()] = line_info[1]
        line = f.readline()
    # Check if all keywords and values are found and set
    for key in hps.keys():
        # If one of the values is None, except nodata_value, the header was not completely read from file
        if hps[key] == None and key != 'nodata_value': raise ASCIIGridError("Incorrect header. Some attributes could not be found: %s" % key, f)
    f.close()
    return hps

def unify_coordinate_fromfile(directory, file_loc, filestr):
    """get data from a raster file
    when the raster is not in the unified form(xllcorner = -180 and yllcorner = -90), standardize the coordinate 
    return the data in the form"""
    
    # read data, and headers
    data = np.array(read_ascii(directory, file_loc, filestr))
    headers = read_headers(directory, file_loc, filestr)
    # get aguements from headers as ncols, nrows, xllcorner, yllcorner, cellsize, nodata_value
    ncols = int(headers['ncols'])
    nrows = int(headers['nrows'])
    xllcorner = float(headers['xllcorner'])
    yllcorner = float(headers['yllcorner'])
    cellsize = float(headers['cellsize'])
    nodata_value = float(headers['nodata_value'])
    
    # Calculate the x and y displacement relete to the standard coordinate (-180,-90); positive value means the data locate at first quadrant
    x_displacement = int((xllcorner+180)//cellsize)
    y_displacement = int((yllcorner+90)//cellsize)

    # get the numbers of rows and columns of standard coordinate
    nrows_unify = int(180 / cellsize)
    ncols_unify = int(360 / cellsize)

    # insert missing columns and delete surplus columns of data(x-axis)
    if x_displacement > 0:
        insert_value_cols = np.full((len(data), x_displacement), nodata_value)
        data = np.insert(data,[0],insert_value_cols,axis=1)
    elif x_displacement < 0:
        data = np.delete(data, np.s_[0:-x_displacement], axis = 1)
    ncols = len(data[0])      
    if ncols > ncols_unify:
        data = np.delete(data, np.s_[ncols_unify:ncols], axis = 1)
    elif ncols < ncols_unify:
        insert_value_cols = np.full((len(data), ncols_unify-ncols), nodata_value)
        data = np.insert(data,[ncols],insert_value_cols,axis=1)
    # insert missing rows and delete surplus rows of data(y-axis)
    if y_displacement > 0:
        insert_value_rows = np.full((y_displacement,len(data[0])), nodata_value)
        data = np.insert(insert_value_rows,0,data,axis=0)
    elif y_displacement < 0:
        data = np.delete(data, np.s_[0:-y_displacement], axis = 0)     
    nrows = len(data)      
    if nrows > nrows_unify:
        data = np.delete(data, np.s_[nrows_unify:nrows], axis = 0)
    elif nrows < nrows_unify:
        insert_value_rows = np.full((nrows_unify-nrows,len(data[0])), nodata_value)
        data = np.insert(data,[0],insert_value_rows,axis=0)        
    return data

# sort to array: sort table which contains element [n * b] into row vectors with n elements with value b
def sort_to_array(data):
    lst = []    #lst is the whole map of cell value
    with open(data) as f:
        # skip the headers
        for _ in range(5):
            next(f)
        # read each line and sort the data
        for line in f:
            # datalst is the list of cellvalue in latitudinal direction
            datalst = []
            # linelst is a list of all the characters in the line 
            linelst = line.split()
            # read each charater in linelst
            for char in linelst:
                # check if it is a cell value or number of cells * the cell value
                searchObj = re.search(r'\*', char, flags=0)
                if searchObj:
                    # expand the cell value to numbered cells
                    cellinfo = re.split(r'\*',char)
                    cellnum = int(cellinfo[0])
                    cellval = float(cellinfo[1])
                    elmlst = [cellval for n in range(cellnum)]
                    datalst.extend(elmlst)
                else:
                    datalst.append(float(char))
            lst.append(datalst)
    arr_data = np.array(lst)
    return arr_data

