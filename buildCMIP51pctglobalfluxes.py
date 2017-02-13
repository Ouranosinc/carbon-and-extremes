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

import Model as Ens
import cdf2ens as c2e
reload(Ens)



datadir='/dmf2/scenario/external_data/CMIP5/'

# Gillet ensemble:
#models=['CanESM2']


#models=['CanESM2']
#models=['MIROC-ESM']
#models=['CanESM2']
#models=['HadGEM2-ES']


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

#missing 'BCC-CSM1-1',


#models=['CanESM2']

# Init an empty mme
mmeglobal=Ens.MME('Global variables and fluxes for the CMIP5 ensemble.')
scen='1pctCO2'
#seas=['ANN','DJF','JJA']
seas=['ANN']
NSEAS=len(seas)
for model in models:

    # Pre-process Atmospheric variables:
    atmvariables=['tas','nbp']
    simdb=c2e.ncdbsearch(datadir,models=[model],variables=atmvariables,scenarios=['1pctCO2'])
    atm=Ens.MME('',simdb)
    atm.AggSeasons(seasons=seas,repair='no')
    alat=atm.Mod(model).lat
    alon=atm.Mod(model).lon

    
    # Pre-process Ocean variables:
    ocvariables=['fgco2']
    simdb=c2e.ncdbsearch(datadir,models=[model],variables=ocvariables)
    oc=Ens.MME('',simdb)
    oc.AggSeasons(seasons=seas,repair='no')
    olat=oc.Mod(model).lat
    olon=oc.Mod(model).lon       

    # Load masks and areas
    lfracdb=c2e.ncdbsearch(datadir,models=[model],variables=['sftlf'])
    aareadb=c2e.ncdbsearch(datadir,models=[model],variables=['areacella'])
    ofracdb=c2e.ncdbsearch(datadir,models=[model],variables=['sftof'])
    oareadb=c2e.ncdbsearch(datadir,models=[model],variables=['areacello'])

    lfracf=Dataset(lfracdb[0]['pathpre']+lfracdb[0]['pathsuf'])
    lfrac=lfracf.variables['sftlf'][:]
    lfrac=lfrac/np.max(lfrac)
    
    aareaf=Dataset(aareadb[0]['pathpre']+aareadb[0]['pathsuf'])
    aarea=aareaf.variables['areacella'][:]
        
    ofracf=Dataset(ofracdb[0]['pathpre']+ofracdb[0]['pathsuf'])
    ofrac=ofracf.variables['sftof'][:]
    ofrac=ofrac/np.max(ofrac)

    oareaf=Dataset(oareadb[0]['pathpre']+oareadb[0]['pathsuf'])
    oarea=oareaf.variables['areacello'][:]
    
    # Init a dummy model
    mod0=Ens.Model(model)

    # Process temperature
    for sea in seas:
        for mem in atm.Mod(model).Mems(scen,'tas'):

            # Reload pre-processed atmospheric variables 
            time=atm.Mod(model).data[scen]['tas'][mem][sea]['time']
            temp=atm.Mod(model).data[scen]['tas'][mem][sea]['series']
            flux0=atm.Mod(model).data[scen]['nbp'][mem][sea]['series']

            # Calculate global average temperature
            totarea=np.sum(np.sum(aarea,axis=1),axis=0)
            wtemp=np.sum(np.sum(temp*aarea,axis=2),axis=1)/totarea

            # Atmosphere to Land carbon flux
            flux=np.sum(np.sum(flux0*aarea*lfrac,axis=2),axis=1)


            # Dump diagnosed variables into dummy model
            mod0.Add2Dic(wtemp,scen=scen,var='tas',mem=mem,sea=sea,typ='global')
            mod0.Add2Dic(time,scen=scen,var='tas',mem=mem,sea=sea,typ='time')     
            mod0.Add2Dic(flux,scen=scen,var='alcf',mem=mem,sea=sea,typ='global')
            mod0.Add2Dic(time,scen=scen,var='alcf',mem=mem,sea=sea,typ='time')


        for mem in oc.Mod(model).Mems(scen,'fgco2'):
            # Reload pre-processed ocean variables         
            time=oc.Mod(model).data[scen]['fgco2'][mem][sea]['time']    
            flux0=oc.Mod(model).data[scen]['fgco2'][mem][sea]['series']    

            #if model in ['BNU-ESM','CanESM2', 'inmcm4']: # Exception, flux in CO2 mass
            if model in ['BNU-ESM','CanESM2']: # Exception, flux in CO2 mass        
                flux0=flux0/(44./12.)

            if flux0[0].shape == ofrac.shape:
                flux=np.sum(np.sum(flux0*oarea*ofrac,axis=2),axis=1)
            else:
                ofrac=1-lfrac
                flux=np.sum(np.sum(flux0*aarea*ofrac,axis=2),axis=1)



            # Append diagnosed variables to dic
            mod0.Add2Dic(flux,scen=scen,var='aocf',mem=mem,sea=sea,typ='global')
            mod0.Add2Dic(time,scen=scen,var='aocf',mem=mem,sea=sea,typ='time')     


    mod0.Map()
    mmeglobal.AddModel(mod0)


# Old convention
#outputfname = '/expl6/leduc/CMIP/Gillet-global-tas_pr_ANN.pkl'

# New convention
output = open('/expl6/leduc/CMIP/CMIP5-global-fluxes-'+scen+'-N'+str(NMOD)+'-'+str(NSEAS)+'seas.pkl', 'wb')

pickle.dump(mmeglobal, output,2)
output.close()



