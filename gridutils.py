from IPython import embed
import numpy as np
import mpl_toolkits
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset

############################################################################
# GRID UTILITIES
############################################################################

def trlonlatdatacmip5(lon,lat,data=None):
    '''Transform lon-lat-data according to basemap rules for plotting.'''

    # Invert data around the horizontal axis
    # if data is not None:
    #     data1=np.flipud(data)
    #     data=data1

    # Convert longitudes to the -180:180 format, not 0:360.
    lon1 = lon.copy()

    for n, l in enumerate(lon1):
        if l >= 180:
           lon1[n]=lon1[n]-360. 
    lon = lon1

    # Reshape lons and data for the first values correspond to -180 deg
    # (split in middle):
    lonmid=lon.shape[0]/2
    lon1 = lon[0:lonmid]
    lon2 = lon[lonmid:]
    lon = np.hstack((lon2, lon1))
    if data is not None:
        if len(data.shape) == 2:
            data1 = data[:,0:lonmid]
            data2 = data[:,lonmid:]
            data = np.hstack((data2, data1))
        elif len(data.shape) == 3:
            Nt,Ny,Nx=data.shape            
            datatmp=np.zeros((Nt,Ny,Nx))
            for tt in np.arange(Nt):
                data1 = data[tt,:,0:lonmid]
                data2 = data[tt,:,lonmid:]
                datatmp[tt,:,:] = np.hstack((data2, data1))
            data=datatmp
        return lon,lat,data
    else:
        return lon,lat


def destgridmodel(modname):
    # Interpolate to a model name

    print '/\/\/\/\==> Interpolating to the '+modname+' grid.'
    
    #nc=Dataset('/home/leduc/data/CMIP5_1pctCO2/areacella_fx_CanESM2_1pctCO2_r0i0p0.nc')
#    nc=Dataset('/dmf2/scenario/external_data/CMIP5/CCCMA/CanESM2/1pctCO2/fx/atmos/r0i0p0/areacella/areacella_fx_CanESM2_1pctCO2_r0i0p0.nc')
    nc=Dataset('/Users/anttii/GoogleDrive/data/tcre2/areacella_fx_CanESM2_1pctCO2_r0i0p0.nc')    
    lon_dest=nc.variables['lon'][:]
    lat_dest=nc.variables['lat'][:]

    # Repair data    
    lon_dest,lat_dest=trlonlatdatacmip5(lon_dest,lat_dest)

    
    return lon_dest,lat_dest

    
def destgridcustom(Xres,Yres,X0=0,Y0=None):
    '''Define custom global grid resolution of Xres x Yres, with X0,Y0 offsets.'''

    if Y0 is None: Y0=Yres/2.

    print '/\/\/\/\==> Interpolating to a custom grid of '+str(Xres)+'x'+str(Yres)
    lon_dest=np.arange(-180+X0,180-X0,Xres)
    lat_dest=np.arange(-90+Y0,91-Y0,Yres)


    #lon,lat,data=trlonlatdatacmip5(lon,lat,data)
    #lon_dest,lat_dest=trlonlatdatacmip5(lon_dest,lat_dest)

    return lon_dest,lat_dest

def interpolateto(data,lon,lat,destgrid):
    '''Interpolate to destgrid, which can be defined as xyres ([Xres,Yres]) or a model name.'''
    
    if isinstance(destgrid,list):
        Xres=destgrid[0]
        Yres=destgrid[1]
        lon_dest,lat_dest=destgridcustom(Xres,Yres)
        
    elif isinstance(destgrid,str):
        if destgrid is 'giss_model_e_r_NA':
            lat_dest=np.array([22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62, 66, 70])

            lon_dest=np.array([-142.5, -137.5, -132.5, -127.5, -122.5, -117.5, -112.5, -107.5,
                               -102.5,  -97.5,  -92.5,  -87.5,  -82.5,  -77.5,  -72.5,  -67.5,
                               -62.5,  -57.5,  -52.5])

        elif destgrid is 'giss_model_e_r_GLB':
            
            lon_dest,lat_dest=destgridcustom(5,4,X0=2.5,Y0=4.)

        elif destgrid is 'hadcrut4':            
            lat_dest=np.array([-87.5, -82.5, -77.5, -72.5, -67.5, -62.5, -57.5, -52.5, -47.5,
                               -42.5, -37.5, -32.5, -27.5, -22.5, -17.5, -12.5,  -7.5,  -2.5,
                               2.5,   7.5,  12.5,  17.5,  22.5,  27.5,  32.5,  37.5,  42.5,
                               47.5,  52.5,  57.5,  62.5,  67.5,  72.5,  77.5,  82.5,  87.5])

            lon_dest=np.array([-177.5, -172.5, -167.5, -162.5, -157.5, -152.5, -147.5, -142.5,
                               -137.5, -132.5, -127.5, -122.5, -117.5, -112.5, -107.5, -102.5,
                               -97.5,  -92.5,  -87.5,  -82.5,  -77.5,  -72.5,  -67.5,  -62.5,
                               -57.5,  -52.5,  -47.5,  -42.5,  -37.5,  -32.5,  -27.5,  -22.5,
                               -17.5,  -12.5,   -7.5,   -2.5,    2.5,    7.5,   12.5,   17.5,
                               22.5,   27.5,   32.5,   37.5,   42.5,   47.5,   52.5,   57.5,
                               62.5,   67.5,   72.5,   77.5,   82.5,   87.5,   92.5,   97.5,
                               102.5,  107.5,  112.5,  117.5,  122.5,  127.5,  132.5,  137.5,
                               142.5,  147.5,  152.5,  157.5,  162.5,  167.5,  172.5,  177.5])

        elif destgrid is 'gpcp':
            lat_dest=np.array([-88.75, -86.25, -83.75, -81.25, -78.75, -76.25, -73.75, -71.25,
                               -68.75, -66.25, -63.75, -61.25, -58.75, -56.25, -53.75, -51.25,
                               -48.75, -46.25, -43.75, -41.25, -38.75, -36.25, -33.75, -31.25,
                               -28.75, -26.25, -23.75, -21.25, -18.75, -16.25, -13.75, -11.25,
                               -8.75,  -6.25,  -3.75,  -1.25,   1.25,   3.75,   6.25,   8.75,
                               11.25,  13.75,  16.25,  18.75,  21.25,  23.75,  26.25,  28.75,
                               31.25,  33.75,  36.25,  38.75,  41.25,  43.75,  46.25,  48.75,
                               51.25,  53.75,  56.25,  58.75,  61.25,  63.75,  66.25,  68.75,
                               71.25,  73.75,  76.25,  78.75,  81.25,  83.75,  86.25,  88.75])


            lon_dest=np.array([   1.25,    3.75,    6.25,    8.75,   11.25,   13.75,   16.25,
                                  18.75,   21.25,   23.75,   26.25,   28.75,   31.25,   33.75,
                                  36.25,   38.75,   41.25,   43.75,   46.25,   48.75,   51.25,
                                  53.75,   56.25,   58.75,   61.25,   63.75,   66.25,   68.75,
                                  71.25,   73.75,   76.25,   78.75,   81.25,   83.75,   86.25,
                                  88.75,   91.25,   93.75,   96.25,   98.75,  101.25,  103.75,
                                  106.25,  108.75,  111.25,  113.75,  116.25,  118.75,  121.25,
                                  123.75,  126.25,  128.75,  131.25,  133.75,  136.25,  138.75,
                                  141.25,  143.75,  146.25,  148.75,  151.25,  153.75,  156.25,
                                  158.75,  161.25,  163.75,  166.25,  168.75,  171.25,  173.75,
                                  176.25,  178.75,  181.25,  183.75,  186.25,  188.75,  191.25,
                                  193.75,  196.25,  198.75,  201.25,  203.75,  206.25,  208.75,
                                  211.25,  213.75,  216.25,  218.75,  221.25,  223.75,  226.25,
                                  228.75,  231.25,  233.75,  236.25,  238.75,  241.25,  243.75,
                                  246.25,  248.75,  251.25,  253.75,  256.25,  258.75,  261.25,
                                  263.75,  266.25,  268.75,  271.25,  273.75,  276.25,  278.75,
                                  281.25,  283.75,  286.25,  288.75,  291.25,  293.75,  296.25,
                                  298.75,  301.25,  303.75,  306.25,  308.75,  311.25,  313.75,
                                  316.25,  318.75,  321.25,  323.75,  326.25,  328.75,  331.25,
                                  333.75,  336.25,  338.75,  341.25,  343.75,  346.25,  348.75,
                                  351.25,  353.75,  356.25,  358.75])
            
            lon_dest=lon_dest-180.            
            
        else:
            lon_dest,lat_dest=destgridmodel(destgrid)
        
        

    # Express lon/lat arrars as matrices
    lon_dest_mat,lat_dest_mat=np.meshgrid(lon_dest,lat_dest)

    
    if len(data.shape) == 2:
        result = mpl_toolkits.basemap.interp(data, lon, lat, lon_dest_mat, lat_dest_mat,
                                             checkbounds=False, masked=False, order=1)
    elif len(data.shape) == 3:
        Nt=data.shape[0]
        Ny_dest,Nx_dest=lon_dest_mat.shape
        result=np.zeros((Nt,Ny_dest,Nx_dest))

        for tt in np.arange(Nt):
            result[tt,:,:] = mpl_toolkits.basemap.interp(data[tt,:,:], lon, lat,
                                                         lon_dest_mat, lat_dest_mat,
                                                         checkbounds=False, masked=False, order=1)

    return result, lon_dest, lat_dest

