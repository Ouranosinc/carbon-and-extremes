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

