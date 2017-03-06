'''Script to generate a multi-model ensemble as a list of model
 objects from a set of .nc files.'''



import matplotlib.pyplot as plt
import sys
from IPython import embed
from netCDF4 import Dataset
import numpy as np
import os
import cPickle as pickle
import numpy.ma as ma # for masks
from itertools import product
import Model as Ens
import cdf2ens as c2e
import netcdfutils
reload(Ens)



datadir='/dmf2/scenario/external_data/CMIP5/'

# Gillet ensemble:
#models=['CanESM2']


#models=['CanESM2']
#models=['MIROC-ESM']
#models=['CanESM2']
#models=['HadGEM2-ES']


#models=[#'BNU-ESM',
        #'CanESM2',
        # 'CESM1-BGC',                    # missing pr
        # 'HadGEM2-ES',                   # missing pr
        # 'inmcm4',
        # 'IPSL-CM5A-LR',
        # 'IPSL-CM5A-MR',
        # 'IPSL-CM5B-LR',
        # 'MIROC-ESM',
        # 'MPI-ESM-LR',
        # 'MPI-ESM-MR',
        # 'NorESM1-ME'
#        ]

#missing 'BCC-CSM1-1',


#models=['CanESM2']

# Init an empty mme
spatialres='global'
scen='rcp85'
scen='1pctCO2'
seas=['ANN','DJF','JJA','SON','MAM']
#seas=['ANN']
NSEAS=len(seas)
var='pr'
#seas=['ANN']


# MODEL SELECTION
# simdb=c2e.ncdbsearch(datadir,realms=['Amon'],models=[],members=['r1i1p1'],variables=[var],scenarios=[scen])
# models0=list(set([simdb[i]['mod'] for i in range(len(simdb))]))

# availability=['MIROC4h',            # Models with areacella field available will be selected from previous list
#               'IPSL-CM5B-LR',
#               'MIROC-ESM',
#               'MIROC5',
#               'CanESM2',
#               'MPI-ESM-MR',
#               'CSIRO-Mk3-6-0',
#               'CESM1-BGC',
#               'inmcm4',
#               'BNU-ESM',
#               'CCSM4',
#               'GFDL-ESM2G',
#               'GFDL-ESM2M',
#               'NorESM1-M',
#               'IPSL-CM5A-MR',
#               'IPSL-CM5A-LR',
#               'CNRM-CM5',
#               'NorESM1-ME',
#               'HadGEM2-ES',
#               'GISS-E2-R',
#               'MRI-CGCM3',
#               'MPI-ESM-LR',
#               'bcc-csm1-1']

# models=[]
# for model in models0:
#     if model in availability:
#         models.append(model)



# RESULT HARDCODED (23 survived, 18 rejected)

# RCP list
models=[
    #'MIROC4h',             # Rejected because covers 200601-203512
    'GFDL-ESM2M',
    'MIROC-ESM',
    'HadGEM2-ES',
    'MPI-ESM-MR',
    'CSIRO-Mk3-6-0',
    'CESM1-BGC',
    'inmcm4',
    'CanESM2',
    'BNU-ESM',
    'IPSL-CM5B-LR',
    'GFDL-ESM2G',
    'CCSM4',
    'NorESM1-M',
    'IPSL-CM5A-MR',
    'IPSL-CM5A-LR',
    'CNRM-CM5',
    'MRI-CGCM3',
    'NorESM1-ME',
    'MIROC5',
    'GISS-E2-R',
    'MPI-ESM-LR',
    'bcc-csm1-1']


# 1pctCO2 ensemble
models=['BNU-ESM',
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


#########################################################################################################

mmeglobal=Ens.MME('Annual series of global averages for '+str(len(models))+' CMIP5 models using '+scen+'.')


for model in models:
    # Pre-process Atmospheric variables:
    atmvariables=[var]
    simdb=c2e.ncdbsearch(datadir,realms=['Amon'],models=[model],members=['r1i1p1'],variables=atmvariables,scenarios=[scen])
    simdb=c2e.simdbrejecttslice(simdb)

    atm=Ens.MME('',simdb)
    atm.AggSeasons(seasons=seas,repair='no')
    alat=atm.Mod(model).lat
    alon=atm.Mod(model).lon

    
    # Load masks and areas
    aareadb=c2e.ncdbsearch(datadir,models=[model],variables=['areacella'])
    if len(aareadb)==0:
        sys.exit('areacella field not found for model '+model)
    aareaf=Dataset(aareadb[0]['pathpre']+aareadb[0]['pathsuf'])
    aarea=aareaf.variables['areacella'][:]

    # Init a dummy model
    mod0=Ens.Model(model)

    # Process temperature
    for sea in seas:
        for mem in atm.Mod(model).Mems(scen,var):

            # Reload pre-processed atmospheric variables 
            time=atm.Mod(model).data[scen][var][mem][sea]['time']
            temp=atm.Mod(model).data[scen][var][mem][sea]['series']

            # Calculate global average temperature
            totarea=np.sum(np.sum(aarea,axis=1),axis=0)
            wtemp=np.sum(np.sum(temp*aarea,axis=2),axis=1)/totarea

            # Dump diagnosed variables into dummy model
            mod0.Add2Dic(wtemp,scen=scen,var=var,mem=mem,sea=sea,typ='global')
            mod0.Add2Dic(time,scen=scen,var=var,mem=mem,sea=sea,typ='time')

    # # Process temperature
    # for sea in seas:
    #     for mem in atm.Mod(model).Mems(scen,'pr'):

    #         # Reload pre-processed atmospheric variables 
    #         time=atm.Mod(model).data[scen]['pr'][mem][sea]['time']
    #         temp=atm.Mod(model).data[scen]['pr'][mem][sea]['series']

    #         # Calculate global average temperature
    #         totarea=np.sum(np.sum(aarea,axis=1),axis=0)
    #         wtemp=np.sum(np.sum(temp*aarea,axis=2),axis=1)/totarea

    #         # Dump diagnosed variables into dummy model
    #         mod0.Add2Dic(wtemp,scen=scen,var='pr',mem=mem,sea=sea,typ='global')
    #         mod0.Add2Dic(time,scen=scen,var='pr',mem=mem,sea=sea,typ='time')                 


    mod0.Map()
    mmeglobal.AddModel(mod0)



ofile = '/home/partanen/data/CMIP5-'+spatialres+'-'+var+'-'+scen+'-N'+str(NMOD)+'-'+str(NSEAS)+'.nc'

datain=[]
varnames=[]
var_longnames=[]
var_units=[]

timelen=0 #Initial value for the length of time axis

gmod={}

varlongnames={}
varlongnames['tas']='temperature'
varlongnames['pr']='precipitation'
units={}
units['tas']='K'
units['pr']='mm day-1'

for model,sea in product(models,seas):

    
    gmod=mmeglobal.Mod(model)

 
    vardata=gmod.data['1pctCO2'][var]['r1i1p1'][sea]['global']
    
    # Convert precipitation from kg m-2 s-1 to mm day-1    
    if var=='pr':
        vardata=86400*vardata

    datain.append(vardata)
    varnames.append(var+'-'+model+'-'+sea)
    var_longnames.append('Global mean '+varlongnames[var]+ ' in ' +sea+' for '+model)
    var_units.append(units[var])

    

    time_len_mod=len(gmod.data['1pctCO2'][var]['r1i1p1']['ANN']['time'].array)
    if time_len_mod>timelen:
        timelen=time_len_mod

timein=np.linspace(1,timelen,timelen)
netcdfutils.write_netcdf_file(datain, varnames, ofile, timein=timein, varnames, var_longnames=var_longnames,
                      var_units=var_units,data_description='Global mean '+varlongnames[var]+' data for the 1pctCO2 scenario from the CMIP5 dataset.')


#pickle.dump(mmeglobal, output,2)
#output.close()
#mmeglobal.Show()



