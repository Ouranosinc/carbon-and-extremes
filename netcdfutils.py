"""
Module containing functions to deal with netCDF data
"""
from __future__ import print_function
import numpy as np
import time
from netCDF4 import Dataset
import os
import sys


def write_netcdf_file(datain, varnames, filename, lat=None, lon=None, timein=None,
                      var_longnames='NetCDF variable',
                      var_units='',
                      time_name='time',
                      time_units='years since 0-1-1 0:0:0',
                      time_longname='time',
                      time_standardname='time',
                      time_calender='noleap',
                      lon_name='lon',
                      lon_longname='longitude',
                      lon_standardname='longitude',
                      lon_units='degrees_east',
                      lon_axis='X',
                      lat_name='lat',
                      lat_longname='latitude',
                      lat_standardname='latitude',
                      lat_units='degrees_north',
                      lat_axis='Y',
                      netcdf_format='NETCDF4',
                      data_description='Data saved from Python'):
    """
    Write a 1D or 2D data into a netCDF file

    Data should be formatted so that it is either ntime for 1D data or 
    ntime x nlat x nlon for 2D data. Other formats will not be saved correctly
    or at all.

    """
    
    # Remove old file
    if os.path.isfile(filename):
        os.remove(filename)    
    
    root_grp = Dataset(filename, 'w', format=netcdf_format)
    

    # Find the length of the time axis if any
    if timein is None:
        timedim = None
    else:
        timedim = len(timein)
        root_grp.createDimension(time_name, timedim)
        times = root_grp.createVariable(time_name, 'f8', (time_name,))

    nvars = len(datain)

    root_grp.description = data_description

    # dimensions
    
    
    if lat is not None:    
        root_grp.createDimension(lat_name, len(lat))
        latitudes = root_grp.createVariable(lat_name, 'f4', (lat_name,))
    
    if lon is not None:
        root_grp.createDimension(lon_name, len(lon))
        longitudes = root_grp.createVariable(lon_name, 'f4', (lon_name,))

    # variables
    vars = [] #Initialize empty list to hold netCDF variables
    
    
    
    
    for i in range(nvars):
        if lat is None:
            vars.append(root_grp.createVariable(varnames[i], 'f4',time_name))
        else:
            vars.append(root_grp.createVariable(varnames[i], 'f4',
                                       (time_name, lat_name, lon_name,)))
        


    

    # Assign values to netCDF variables
    if lat is not None: latitudes[:] = lat
    if lon is not None: longitudes[:] = lon
    if timein is not None: times[:] = timein
    
        
    
    for i in range(nvars):
        if np.ndim(datain[i])==1:                        
            time_in_len=len(datain[i])            
            vars[i][:]=np.NaN
            vars[i][0:time_in_len] = datain[i]
        elif np.ndim(datain[i])==3:
            time_in_len=datain[i].shape[0]
            vars[i][:,:,:]=np.NaN
            vars[i][0:time_in_len,:,:] = datain[i]
        else:
            print('Unsupported dimension for the variable. Exiting.')
            sys.exit()

    # Define attributes
    if timein is not None:
        times.units = time_units
        times.long_name = time_longname
        times.standard_name = time_standardname
        times.calender = time_calender

    if lon is not None:    
        longitudes.long_name = lon_longname
        longitudes.standard_name = lon_standardname
        longitudes.units = lon_units

    if lat is not None:    
        latitudes.long_name = lat_longname
        latitudes.standard_name = lat_standardname
        latitudes.units = lat_units


    for i in range(nvars):
        vars[i].long_name = var_longnames[i]
        if type(var_units) is list:                  
            vars[i].units = var_units[i]
        else:
            vars[i].units = var_units

    

    root_grp.history = 'Created ' + time.ctime(time.time())
    root_grp.source = 'CMIP5 archieve'
    root_grp.contact='antti-ilari.partanen@concordia.ca'

    root_grp.close()
