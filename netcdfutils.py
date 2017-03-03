"""
Module containing functions to deal with netCDF data
"""

import numpy as np
import time
from netCDF4 import Dataset
import os


def write_1d_netcdf_file(datain, timein, filename, varnames,
                      var_longnames=['NetCDF variable'],
                      var_units=['not defined'],
                      var_missing_value=np.NaN,
                      var_fill_value=np.NaN,
                      time_name='time',
                      time_units='year',
                      time_longname='time',
                      time_standardname='time',
                      time_calender='noleap',
                      netcdf_format='NETCDF4',
                      data_description='Data saved from Python'):
    """
    Write netCDF file in for the UVic ESCM. Variables datain, varnames, and
    var_longname should be a list of numpy arrays.
    """

    # Remove old file
    if os.path.isfile(filename):
        os.remove(filename)

    root_grp = Dataset(filename, 'w', format=netcdf_format)
    

    # Find the length of the time axis if any
    if (np.ndim(np.squeeze(datain[0])) > 2):
        timedim = np.shape(np.squeeze(datain[0]))[2]
    else:
        timedim = None

    nvars = len(datain)

    # dimensions
    root_grp.createDimension('time', timedim)

    # variables
    vars = []  # Initialize empty dict to hold netcdf variables
    times = root_grp.createVariable(time_name, 'f8', (time_name,))

    for i in range(nvars):
        vars.append(root_grp.createVariable(varnames[i], 'f4',
                                            (time_name,)))

    times[:] = timein

    for i in range(nvars):
        vars[i][:] = datain[i]

    # Define attributes
    times.units = time_units
    times.long_name = time_longname
    times.standard_name = time_standardname
    times.calender = time_calender

    for i in range(nvars):
        vars[i].long_name = var_longnames[i]
        vars[i].units = var_units[i]
        vars[i].FillValue = var_fill_value
        vars[i].missing_value = var_fill_value

    root_grp.description = data_description
    root_grp.history = 'Created ' + time.ctime(time.time())
    root_grp.source = 'CMIP5 archieve'
    root_grp.contact='antti-ilari.partanen@concordia.ca'
    
    root_grp.close()
    
def write_2d_netcdf_file(datain, lat, lon, timein, filename, varnames,
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
    Write a 2D netCDF file

    Data should be formatted so that it is ntime x nlat x nlon. Lat index 0 
    refers to XX and lon index 0 refers to XX

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

    nvars = len(datain)

    root_grp.description = data_description

    # dimensions
    root_grp.createDimension(time_name, timedim)
    root_grp.createDimension(lat_name, len(lat))
    root_grp.createDimension(lon_name, len(lon))
    

    # variables
    vars = [] #Initialize empty list to hold netCDF variables
    times = root_grp.createVariable(time_name, 'f8', (time_name,))
    latitudes = root_grp.createVariable(lat_name, 'f4', (lat_name,))
    longitudes = root_grp.createVariable(lon_name, 'f4', (lon_name,))
    
    for i in range(nvars):
        vars.append(root_grp.createVariable(varnames[i], 'f4',
                                       (time_name, lat_name, lon_name,)))
        


    

    # Assign values to netCDF variables
    latitudes[:] = lat
    longitudes[:] = lon
    times[:] = timein
    
        
    
    for i in range(nvars):
        time_in_len=datain[i].shape[0]
        vars[i][:,:,:]=np.NaN
        vars[i][0:time_in_len,:,:] = datain[i]  

    # Define attributes
    times.units = time_units
    times.long_name = time_longname
    times.standard_name = time_standardname
    times.calender = time_calender
    longitudes.long_name = lon_longname
    longitudes.standard_name = lon_standardname
    longitudes.units = lon_units


    for i in range(nvars):
        vars[i].long_name = var_longnames[i]
        if type(var_units) is list:                  
            vars[i].units = var_units[i]
        else:
            vars[i].units = var_units

    latitudes.units = lat_units

    root_grp.history = 'Created ' + time.ctime(time.time())
    root_grp.source = 'CMIP5 archieve'

    # lat.units = 'degrees north'
    # lon.units = 'degrees east'

    root_grp.close()

