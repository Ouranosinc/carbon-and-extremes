'''Script to generate a multi-model ensemble as a list of model objects from a set of .nc files.

For simulations given as time slices, files are appended so are assumed to be given in chronological order from the ncdfinfo5 function.

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
#from Ensemble import Model
reload(Ens)



# !!!!!!!!!! Select also var and scen
# var='tas'
# scen='1pctCO2'
#xyres=[3.75,3.]
#destgrid=[3.75,3.75]
destgrid='CanESM2'

# Select in which format the output is saved
output_netcdf=True
output_pickle=True

# Gillet ensemble:
# models=['BCC-CSM1-1','BNU-ESM','CanESM2','CESM1-BGC','GFDL-ESM2G','GFDL-ESM2M','HadGEM2-ES','INMCM4','IPSL-CM5A-LR','IPSL-CM5A-MR','IPSL-CM5B-LR','MIROC-ESM','MPI-ESM-LR','MPI-ESM-MR','NorESM1-ME'] # 

models=[
     'BNU-ESM',
    # 'CanESM2',
    # 'CESM1-BGC',
    # 'HadGEM2-ES',
    #'inmcm4',
    # 'IPSL-CM5A-LR',
    # 'IPSL-CM5A-MR',
    # 'IPSL-CM5B-LR',
    # 'MIROC-ESM',
    # 'MPI-ESM-LR',
    # 'MPI-ESM-MR',
    # 'NorESM1-ME'
    ]

NMOD=len(models)

#models=['CanESM2']

var='pr'
#var='pr'
scen='1pctCO2'
mem='r1i1p1'
datadir='/dmf2/scenario/external_data/CMIP5/'
#seas=['ANN','DJF','JJA','SON','MAM']
seas=['ANN']
NSEAS=len(seas)

simdb=c2e.ncdbsearch(datadir,models=models,variables=[var],scenarios=[scen])
#sys.exit()

# # Create MME object

mme=Ens.MME('Earth System Models from the CMIP5 1pctCO2 experiment.',simdb)
mme.AggSeasons(seasons=seas)
mme.Interpolate(destgrid,seas)
mme.Resolution()

# Write mme to file
#output = open('/home/leduc/data/CMIP/gilletMME-1pctCO2-3_75x3.pkl', 'wb')
#output = open('/home/leduc/data/CMIP/gilletMME-1pctCO2-3_75x3_75.pkl', 'wb')
#output = open('/home/leduc/data/CMIP/gilletMME-1pctCO2-2_8x2_8.pkl', 'wb')

# New convention
#outputfname = '/home/partanen/data/CMIP5-'+'regional'+'-'+var+'-'+scen+'-N'+str(NMOD)+'-'+str(NSEAS)+'seas.pkl'
#output = open(outputfname, 'wb')
#
#pickle.dump(mme, output,2)
#output.close()


datain=[]
varnames=[]
var_longnames=[]
var_units=[]

timelen=0 #Initial value for the length of time axis


for model,sea in product(models, seas):

    mod=mme.Mod(model)
    Tl=mod.data[scen][var][mem][sea]['series']

    tts0=mod.data[scen][var][mem][sea]['time'].array
    lat=mod.lat
    lon=mod.lon
   

    datain.append(Tl)
    varnames.append(var+'-'+model+'-'+sea)
    var_longnames.append('Global mean temperature in '+sea+' for '+model)
    var_units.append('K')

#    print(len(tts0)) 

#
#    # Add precipitation and convert it from kg m-2 s-1 to mm day-1
#    datain.append(gmod['pr'].data['1pctCO2']['pr']['r1i1p1'][sea]['global']*86400)
#    varnames.append('pr'+'-'+model+'-'+sea)
#    var_longnames.append('Global mean precipitation in '+sea+' for '+model)
#    var_units.append('mm day-1')
#
#      
#
    time_len_mod=len(tts0)
    if time_len_mod>timelen:
        timelen=time_len_mod

if output_netcdf:
    outputfile_netcdf = ('/home/partanen/data/CMIP5-'+'regional'+'-'+var+'-'+scen+'-N'+str(NMOD)+'-'+str(NSEAS)+'seas.nc')
    timein=np.linspace(1,timelen,timelen)
    netcdfutils.write_netcdf_file(datain,varnames, outputfile_netcdf, lat=lat, lon=lon, timein=timein, var_longnames=var_longnames,
                      var_units=var_units,data_description='Annual series of temperature for the 1pctCO2 scenario from the CMIP5 dataset.')
if output_pickle:
    outputfile_pickle='/home/partanen/data/CMIP5-'+'regional'+'-'+var+'-'+scen+'-N'+str(NMOD)+'-'+str(NSEAS)+'seas.pkl'
    output = open(outputfile_pickle, 'wb')
    pickle.dump(mme, output,2)
