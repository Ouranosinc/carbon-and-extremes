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

import Model as Ens
import cdf2ens as c2e
#from Ensemble import Model
reload(Ens)



# !!!!!!!!!! Select also var and scen
# var='tas'
# scen='1pctCO2'
#xyres=[3.75,3.]
#destgrid=[3.75,3.75]
destgrid='CanESM2'




# Gillet ensemble:
# models=['BCC-CSM1-1','BNU-ESM','CanESM2','CESM1-BGC','GFDL-ESM2G','GFDL-ESM2M','HadGEM2-ES','INMCM4','IPSL-CM5A-LR','IPSL-CM5A-MR','IPSL-CM5B-LR','MIROC-ESM','MPI-ESM-LR','MPI-ESM-MR','NorESM1-ME'] # 

models=[
    # 'BNU-ESM',
    # 'CanESM2',
    # 'CESM1-BGC',
    # 'HadGEM2-ES',
    'inmcm4',
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

vv='pr'
#vv='pr'
scen='1pctCO2'
datadir='/dmf2/scenario/external_data/CMIP5/'
#seas=['ANN','DJF','JJA','SON','MAM']
seas=['ANN']
NSEAS=len(seas)

simdb=c2e.ncdbsearch(datadir,models=models,variables=[vv],scenarios=[scen])
sys.exit()

# # Create MME object

mme=Ens.MME('Earth System Models from the CMIP5 1pctCO2 experiment.',simdb)
mme.AggSeasons(seasons=seas)
mme.Interpolate(destgrid)
mme.Resolution()

# Write mme to file
#output = open('/home/leduc/data/CMIP/gilletMME-1pctCO2-3_75x3.pkl', 'wb')
#output = open('/home/leduc/data/CMIP/gilletMME-1pctCO2-3_75x3_75.pkl', 'wb')
#output = open('/home/leduc/data/CMIP/gilletMME-1pctCO2-2_8x2_8.pkl', 'wb')

# New convention
outputfname = '/expl6/leduc/CMIP/CMIP5-'+'regional'+'-'+vv+'-'+scen+'-N'+str(NMOD)+'-'+str(NSEAS)+'seas.pkl'
output = open(outputfname, 'wb')

pickle.dump(mme, output,2)
output.close()





