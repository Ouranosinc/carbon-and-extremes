
import cPickle as pickle
import numpy as np
import Emissions as emi
from itertools import product
import netcdfutils


gddir = '/Users/anttii/GoogleDrive/'


datadir = gddir + 'data/tcre2/'
scen='1pctCO2'

mem='r1i1p1'


vars=['tas', 'pr']
seas=['JJA','SON','MAM', 'DJF', 'ANN']


pklglob_tas=datadir+'CMIP5-global-tas-1pctCO2-N12-5seas.pkl'
pklglob_pr=datadir+'CMIP5-global-pr-1pctCO2-N12-5seas.pkl'                 
pklglob_fluxes=datadir+'CMIP5-global-fluxes-1pctCO2-N12-1seas.pkl'       
         

mmeg={}

output = open(pklglob_tas, 'rb')
mmeg['tas']=pickle.load(output)
output.close()

output = open(pklglob_pr, 'rb')
mmeg['pr']=pickle.load(output)
output.close()

output = open(pklglob_fluxes, 'rb')
mmeg['fluxes']=pickle.load(output)
output.close()


models=mmeg['tas'].Models()







ofile='/Users/anttii/GoogleDrive/data/tcre-nonCO2/netcdf-test.nc'

datain=[]
varnames=[]
var_longnames=[]
var_units=[]

timelen=0 #Initial value for the length of time axis

for model,sea in product(models, seas):

    gmod={}
    
    gmod['tas']=mmeg['tas'].Mod(model)
    gmod['pr']=mmeg['pr'].Mod(model)
    gmod['fluxes']=mmeg['fluxes'].Mod(model)    


    datain.append(gmod['tas'].data['1pctCO2']['tas']['r1i1p1'][sea]['global'])
    varnames.append('tas'+'-'+model+'-'+sea)
    var_longnames.append('Global mean temperature in '+sea+' for '+model)
    var_units.append('K')

    # Add precipitation and convert it from kg m-2 s-1 to mm day-1
    datain.append(gmod['pr'].data['1pctCO2']['pr']['r1i1p1'][sea]['global']*86400)
    varnames.append('pr'+'-'+model+'-'+sea)
    var_longnames.append('Global mean precipitation in '+sea+' for '+model)
    var_units.append('mm day-1')

    if sea=='ANN':
        # Calculate cumulative emissions
        C,ALC,AOC=emi.getCO2fluxes(gmod['fluxes'])
        DC,Lcum,Ocum,E=emi.cfluxes2budget(C,ALC,AOC)

        datain.append(E)
        varnames.append('cum_co2_emi'+'-'+model)
        var_longnames.append('Cumulative carbon emissions for '+model)
        var_units.append('Tt C')    

    time_len_mod=len(gmod['tas'].data['1pctCO2']['tas']['r1i1p1']['ANN']['time'].array)
    if time_len_mod>timelen:
        timelen=time_len_mod

timein=np.linspace(1,timelen,timelen)
netcdfutils.write_1d_netcdf_file(datain, timein, ofile, varnames, var_longnames=var_longnames,
                      var_units=var_units,data_description='Global mean temperature and precipiation data with cumulative carbon emissions for the 1pctCO2 scenario from the CMIP5 dataset.')


