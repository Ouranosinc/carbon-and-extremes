'''Script to generate a multi-model ensemble as a list of model objects from
a set of .nc files.

For simulations given as time slices, files are appended so are assumed to be
given in chronological order from the ncdfinfo5 function.

(working from Ouranos workstation)
'''


import matplotlib.pyplot as plt
import sys
from IPython import embed
from netCDF4 import Dataset
import numpy as np
import os
import cPickle as pickle
from itertools import product

import Model as Ens
import cdf2ens as c2e
import netcdfutils

reload(Ens)

#Select the grid to interpolate onto
destgrid='CanESM2'

# Select in which format the output is saved
output_netcdf=True
output_pickle=True

# Models for the ensemble ensemble:
models=[
     'BNU-ESM',
     'CanESM2',
     'CESM1-BGC',
     'HadGEM2-ES',
     'inmcm4',
     'IPSL-CM5A-LR',
     'IPSL-CM5A-MR',
     'IPSL-CM5B-LR',
     'MIROC-ESM',
     'MPI-ESM-LR',
     'MPI-ESM-MR',
     'NorESM1-ME'
     ]

NMOD=len(models)

var='pr'
scen='1pctCO2'
mem='r1i1p1'
datadir='/dmf2/scenario/external_data/CMIP5/'
outputdir='/home/partanen/data/'
seas=['ANN','DJF','JJA','SON','MAM']

NSEAS=len(seas)

if var=='tas':
    varlong='temperature'
    units='K'
elif var=='pr':
    varlong='precipitation'
    units='mm day-1'

simdb=c2e.ncdbsearch(datadir,models=models,variables=[var],scenarios=[scen])


# # Create MME object
mme=Ens.MME('Earth System Models from the CMIP5 1pctCO2 experiment.',simdb)
mme.AggSeasons(seasons=seas)
mme.Interpolate(destgrid,seas)
mme.Resolution()

# Variables used to save data into netCDF format
datain=[] # List of variables
varnames=[] # List of variable names
var_longnames=[] # List of Long names for the variables
var_units=[] # List of units for variables

timelen=0 #Initial value for the length of time axis


for model,sea in product(models, seas):

    mod=mme.Mod(model)
    Tl=mod.data[scen][var][mem][sea]['series']

    # Convert precipitation from kg m-2 s-1 to mm day-1
    if var=='pr':
        Tl=Tl*86400

    tts0=mod.data[scen][var][mem][sea]['time'].array
    lat=mod.lat
    lon=mod.lon
   
    datain.append(Tl)
    varnames.append(var+'-'+model+'-'+sea)
    var_longnames.append('Mean ' + varlong + ' in '+sea+' for '+model)
    var_units.append(units)

    
    # Save length for time axis if given model has more time-steps than previous models
    time_len_mod=len(tts0)
    if time_len_mod>timelen:
        timelen=time_len_mod

if output_netcdf:
    outputfile_netcdf = (outputdir+'CMIP5-'+'regional'+'-'+var+'-'+scen+'-N'+str(NMOD)+
                         '-'+str(NSEAS)+'seas.nc')
    timein=np.linspace(1,timelen,timelen)

    data_description=('Annual series of ' + varlong + 
                      ' for the 1pctCO2 scenario from the CMIP5 dataset.')

    netcdfutils.write_netcdf_file(datain,varnames, outputfile_netcdf, lat=lat, lon=lon,
                                  timein=timein, var_longnames=var_longnames,
                                  var_units=var_units, data_description=data_description)
if output_pickle:
    outputfile_pickle=(outputdir+'CMIP5-'+'regional'+'-'+var+'-'+scen+'-N'+str(NMOD)+'-'+
                       str(NSEAS)+'seas.pkl')
    
    output = open(outputfile_pickle, 'wb')
    pickle.dump(mme, output,2)
    output.close()
