
import cPickle as pickle
import numpy as np
import os
from netCDF4 import Dataset
import time
import Emissions as emi
from itertools import product



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
write_1d_netcdf_file(datain, timein, ofile, varnames, var_longnames=var_longnames,
                      var_units=var_units,data_description='Global mean temperature and precipiation data with cumulative carbon emissions for the 1pctCO2 scenario from the CMIP5 dataset.')


