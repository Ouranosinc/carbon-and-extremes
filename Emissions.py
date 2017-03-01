import matplotlib.pyplot as plt
import sys
from IPython import embed
import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset

#import classModel.Ensemble as Ens
import Model as Ens
import gridutils as gu

from tcre5 import *


def AggYears(ts,data,t0,t1,dt):
    '''WORK WITH TIME INDICES RATHER THAN YEARS. Create custom time axis based on t0,t1 and dt.     y1 not included in the range so nyears = y1-y0'''
    
    if (t1 - t0)%dt == 0:
        # Trim data
        ts=ts[t0:t1]
        data=data[t0:t1]

        ndt=(t1 - t0)/dt
        tclim=np.zeros(ndt)

        try: 
            ny,nx=data.shape[1],data.shape[2]
            dclim=np.zeros((ndt,ny,nx))
        except:
            dclim=np.zeros(ndt)            
        
        if dt==1:
            shift=0.
        else:
            shift=1./2


        
        for pp in range(ndt):
            tclim[pp]=t0+(pp+shift)*dt
            dclim[pp]=np.mean(data[range(pp*dt,(pp+1)*dt)],0)
                
        return tclim,dclim

        
    else:
        sys.exit('Averaging window incompatible with time range.')



def cumula(data):
    n=data.shape[0]
    cdata=np.zeros(n)
    for i in range(1,n):
        cdata[i]=data[i]+cdata[i-1]

    return cdata




def cfluxes2budget(C,ALC,AOC,t0=0):

    C=C[t0:]
    ALC=ALC[t0:]
    AOC=AOC[t0:]
        
    Lcum=cumula(ALC)
    Ocum=cumula(AOC)
    DC=C-C[0]

    E=DC+Lcum+Ocum
    
    return DC,Lcum,Ocum,E


def getCO2fluxes(gmod,scen='1pctCO2',mem='r1i1p1',sea='ANN'):
    C0=285.*2.13/1000.                           #in Tt C
    kg2tt=1E-15

    tts=gmod.data[scen]['tas'][mem][sea]['time'].array
    Nt=tts.shape[0]
    C=C0+np.zeros(Nt)
    for tt in range(1,Nt):
        C[tt]=C[tt-1]*1.01

    
    nsy=gmod.data[scen]['tas'][mem][sea]['time'].ndy*60*60*24
    ALC=gmod.data[scen]['alcf'][mem][sea]['global']*kg2tt*nsy
    AOC=gmod.data[scen]['aocf'][mem][sea]['global']*kg2tt*nsy


    E=(ALC+AOC+(C-C[0]))
    
    return C,ALC,AOC


#############    
def CO2fluxes1pct(gmod,scen='1pctCO2',mem='r1i1p1',sea='ANN'):

    C0=285.*2.13/1000.                           #in Tt C
    kg2tt=(1E-15)

    tts=gmod.data[scen]['tas'][mem][sea]['time'].array
    Nt=tts.shape[0]
    C=C0+np.zeros(Nt)
    for tt in range(1,Nt):
        C[tt]=C[tt-1]*1.01

    
    nsy=gmod.data[scen]['tas'][mem][sea]['time'].ndy*60*60*24
    ALC=cumula(gmod.data[scen]['alcf'][mem][sea]['global'])*kg2tt*nsy
    AOC=cumula(gmod.data[scen]['aocf'][mem][sea]['global'])*kg2tt*nsy

    DC=C-C[0]
    E=(ALC+AOC+DC)
    
    return C,ALC,AOC,E








def trimdomain(lon0,lat0,data0,lonbounds,latbounds):
    '''Trim domain between lon and lat boundaries.'''

    loni=np.where(np.logical_and(lon0>=lonbounds[0], lon0<=lonbounds[1]))[0]
    lati=np.where(np.logical_and(lat0>=latbounds[0], lat0<=latbounds[1]))[0]

    nx=len(loni)
    ny=len(lati)

    lon=lon0[loni]
    lat=lat0[lati]
    
    lon=lon0[lon0>=lonbounds[0]]
    lon=lon[lon<lonbounds[1]]             # removed =

    lat=lat0[lat0>=latbounds[0]]
    lat=lat[lat<latbounds[1]]             # removed =

    if len(data0.shape)==2:
        ny0,nx0=data0.shape    
        data=np.zeros((ny,nx))
        i=0
        for xx in loni:
            j=0
            for yy in lati:
                data[j,i]=data0[yy,xx]
                j+=1
            i+=1
    
    if len(data0.shape)==3:
        nt0,ny0,nx0=data0.shape    
        data=np.zeros((nt0,ny,nx))
        for tt in range(nt0):
            i=0
            for xx in loni:
                j=0
                for yy in lati:
                    data[tt,j,i]=data0[tt,yy,xx]
                    j+=1
                i+=1

                

    return lon,lat,data


def myregionsbounds(label):
    '''Return lon/lat boundaries of regions.'''

    # My regions
    if label is 'Qc':
        name='Quebec'
        lonb=[-80.,-60.]
        latb=[45.,63.]
    elif label == 'Alaska':
        lonb=[-165,-140]
        latb=[55.5,70.5]
    elif label == 'Brazil':
        lonb=[-73,-37.5]
        latb=[-20,1.5]
    elif label == 'Australia':
        lonb=[112,154]
        latb=[-40.5,-10.5]
    elif label == 'China':
        lonb=[90,120]
        latb=[25,42]
    elif label == 'Europe':
        lonb=[-10,30]
        latb=[35,70]        
    elif label ==  'SouthAfrica':
        lonb=[12,32]
        latb=[-35,-26]
    elif label == 'ARC':
        lonb=[-180,180]
        latb=[70,90]
    elif label == 'Western_US':
        lonb=[-125.,-105.]        
        latb=[25,45]
    elif label is 'ANT': 
        name='Antarctica'             
        lonb=[-180,180]
        latb=[-90,-60]
        
    return np.array(lonb),np.array(latb)



        
# Giorgi Regions
def giorgibounds(label):
    '''Return lon/lat boundaries of Giorgis regions.'''


    if label is 'AUS': 
        name='Australia'              
        latb=['45S', '11S'] 
        lonb=['110E', '155E'] 

    elif label is 'AMZ': 
        name='Amazon Basin'           
        latb=['20S', '12N'] 
        lonb=['82W', '34W']   

    elif label is 'SSA': 
        name='Southern South America' 
        latb=['56S', '20S'] 
        lonb=['76W', '40W']   

    elif label is 'CAM': 
        name='Central America'        
        latb=['10N', '30N'] 
        lonb=['116W', '83W']  

    elif label is 'WNA': 
        name='Western North America'   
        latb=['30N', '60N'] 
        lonb=['130W', '103W'] 

    elif label is 'CNA': 
        name='Central North America'   
        latb=['30N', '50N'] 
        lonb=['103W', '85W']  

    elif label is 'ENA': 
        name='Eastern North America'   
        latb=['25N', '50N'] 
        lonb=['85W', '60W']   

    elif label is 'ALA': 
        name='Alaska'
        latb=['60N', '72N'] 
        lonb=['170W', '103W'] 

    elif label is 'GRL':
        name='Greenland'
        latb=['50N', '85N'] 
        lonb=['103W', '10W']  

    elif label is 'MED': 
        name='Mediterranean Basin'    
        latb=['30N', '48N'] 
        lonb=['10W', '40E']   

    elif label is 'NEU': 
        name='Northern Europe'        
        latb=['48N', '75N'] 
        lonb=['10W', '40E']   

    elif label is 'WAF': 
        name='Western Africa'         
        latb=['12S', '18N'] 
        lonb=['20W', '22E']   

    elif label is 'EAF': 
        name='Eastern Africa'         
        latb=['12S', '18N'] 
        lonb=['22E', '52E']   

    elif label is 'SAF': 
        name='Southern Africa'        
        latb=['35S', '12S'] 
        lonb=['10W', '52E']   

    elif label is 'SAH': 
        name='Sahara'                 
        latb=['18N', '30N'] 
        lonb=['20W', '65E']   

    elif label is 'SEA': 
        name='Southeast Asia'         
        latb=['11S', '20N'] 
        #lonb=['95E', '155E']
        lonb=['100E', '155E']          

    elif label is 'EAS': 
        name='East Asia'              
        latb=['20N', '50N'] 
        lonb=['100E', '145E'] 

    elif label is 'SAS': 
        name='South Asia'             
        latb=['5N ', '30N'] 
        lonb=['65E', '100E']  

    elif label is 'CAS': 
        name='Central Asia'           
        latb=['30N', '50N'] 
        lonb=['40E', ' 75E']  

    elif label is 'TIB': 
        name='Tibet'                  
        latb=['30N', '50N'] 
        lonb=['75E', '100E']  

    elif label is 'NAS': 
        name='North Asia'             
        latb=['50N', '70N'] 
        lonb=['40E', '180E']
        
    else:
        return 0

    # Convert lat strings to real coordinates
    latb2=[0.,0.]
    i=0
    for la in latb:
        if 'N' in la:
            latb2[i]=float(la.split('N')[0])
        elif 'S' in la:
            latb2[i]=-float(la.split('S')[0])

        i+=1

    # Convert lon strings to real coordinates
    lonb2=[0.,0.]
    j=0
    for lo in lonb:
        if 'E' in lo:
            lonb2[j]=float(lo.split('E')[0])
        elif 'W' in lo:
            lonb2[j]=-float(lo.split('W')[0])

        j+=1     

        

    return np.array(lonb2),np.array(latb2)


# Ocean Regions
def oceanbounds(label):
    '''Return 2 arrays for lon and lat boundaries of rectangular oceans.'''

    if label=='SPO':
        lonb=[145,-70]
        #lonb=[0,40]
        latb=[-60,0]
    elif label=='NPO':
        lonb=[116,-70]
        latb=[0,68]        
    elif label=='SAO':
        lonb=[-70,20]
        latb=[-60,0]        
    elif label=='NAO':
        lonb=[-98,12]
        latb=[0,68]        
    elif label=='IO':
        lonb=[20,145]
        latb=[-60,31]        
    elif label=='AO':
        lonb=[-180,180]
        latb=[68,90]        
    elif label=='SO':
        lonb=[-180,180]
        latb=[-90,-60]        
        
    return np.array((lonb)), np.array((latb))

def maskregion(lon,lat,data,reg):
    # Return masked array of data.
    
    ndim=data.ndim
    
    if reg in giorgiregions:
        lonb,latb=giorgibounds(reg)
        regmask=maskregregion(lon,lat,lonb,latb)
        mask=mergemasks(regmask,lsmask)            #2D mask
        if ndim==3:
            mask=np.array([mask,]*data.shape[0])   #extend mask over time axis
    elif reg in mylandregions:
        lonb,latb=myregionsbounds(reg)
        regmask=maskregregion(lon,lat,lonb,latb)
        mask=mergemasks(regmask,lsmask)            #2D mask
        if ndim==3:
            mask=np.array([mask,]*data.shape[0])   #extend mask over time axis            
    elif reg in oceanregions:
        lonb,latb=oceanbounds(reg)
        regmask=maskregregion(lon,lat,lonb,latb)     # Ocean rectangle
        regmask1=correctocean(lon,lat,lonb,latb,reg)    # Ocean correction
        regmask=regmask+regmask1
        
        mask=mergemasks(regmask,1-lsmask)            #2D mask
        if ndim==3:
            mask=np.array([mask,]*data.shape[0])   #extend mask over time axis            
            
    elif reg in arearegions:
        lonb,latb=myregionsbounds(reg)
        mask=maskregregion(lon,lat,lonb,latb)
        if ndim==3:
            mask=np.array([mask,]*data.shape[0])   #extend mask over the time axis        
    else:
        mask=maskcompositeregion(lon,lat,reg)
        if ndim==3:        
            mask=np.array([mask,]*data.shape[0])   #extend mask over the time axis
        
    data=np.ma.masked_array(data,mask=mask)

    return data
    

def maskcompositeregion(lon,lat,compreg):
    # Mask composite region

    if compreg == 'LND':
        mask=lsmask                       #0 on land
    elif compreg == 'OCN':
        mask=1-lsmask
    elif compreg == 'LND-ARC':
        lonb,latb=myregionsbounds('ARC')
        regmask=maskregregion(lon,lat,lonb,latb)
        mask=lsmask + (1-regmask)
        mask=mask/np.max(mask)                
    elif compreg == 'OCN-ARC':
        lonb,latb=myregionsbounds('ARC')
        regmask=maskregregion(lon,lat,lonb,latb)
        mask=(1-lsmask) + (1-regmask)
        mask=mask/np.max(mask)                
    elif compreg == 'GLB-ARC':
        lonb,latb=myregionsbounds('ARC')
        regmask=maskregregion(lon,lat,lonb,latb)
        mask=1-regmask
    elif compreg == 'GLB':
        mask=np.zeros((lat.__len__(),lon.__len__()))
    elif compreg == 'none':
        mask=np.ones((lat.__len__(),lon.__len__()))        
        

    return mask

def correctocean(lon0,lat0,lonbounds,latbounds,reg):    # Ocean correction
    ''' maxk with +1 to active mask, -1 to unmask and 0 to do nothing.'''
    
    ny,nx=len(lat0),len(lon0)

    mask=np.zeros((ny,nx))
    i=0
    for xx in np.arange(len(lon0)):
        for yy in np.arange(len(lat0)):
            if reg=='NPO':
                if ((lon0[xx]>=-100 and lon0[xx]<-71 and lat0[yy]>=40) or
                   (lon0[xx] >= -96 and lon0[xx]<-50 and lat0[yy]>=18) or
                   (lon0[xx] >= -82 and lon0[xx]<-50 and lat0[yy]>=11) or
                   (lon0[xx]>=105 and lon0[xx] < 130  and lat0[yy]<15)):
                    
                    mask[yy,xx]=1

            if reg=='NAO':
                if ((lon0[xx]<-84 and lat0[yy]<16) or
                    (lon0[xx]<-73 and lat0[yy]<10) or
                    (lon0[xx]>=-100 and lon0[xx]<-71 and lat0[yy]>=40) or
                    (lon0[xx]>=0 and lat0[yy]<45 and lat0[yy]>30)):
                    
                    mask[yy,xx]=1

            if reg=='IO':
                if ((lon0[xx]>=100 and lat0[yy]>=-11)):
                    
                    mask[yy,xx]=1                    
                
    return mask


    
def maskregregion(lon0,lat0,lonbounds,latbounds):
    '''Given a map with lon0 and lat0 coordinates, maskregion returns mask around the region defined by lonbounds and latbounds. By default, 0 are given over the regions (mask off) and 1 (mask on) everywhere.'''
    
    ny,nx=len(lat0),len(lon0)

    if lonbounds[0] > lonbounds[1]:
        loni1=np.where(np.logical_and(lon0>=lonbounds[0], lon0<180.))[0]
        loni=np.where(np.logical_and(lon0>=-180, lon0<lonbounds[1]))[0]
        #embed()
        #loni=loni1
        loni=np.concatenate((loni,loni1))
    else:
        loni=np.where(np.logical_and(lon0>=lonbounds[0], lon0<lonbounds[1]))[0]
                
    lati=np.where(np.logical_and(lat0>=latbounds[0], lat0<latbounds[1]))[0]
    

    mask=np.ones((ny,nx))
    i=0
    for xx in loni:
        for yy in lati:
            mask[yy,xx]=0.

    return mask



# def maskregregion(lon0,lat0,lonbounds,latbounds):
#     '''Given a map with lon0 and lat0 coordinates, maskregion returns mask around the region defined by lonbounds and latbounds. By default, 0 are given over the regions (mask off) and 1 (mask on) everywhere.'''
    
#     ny,nx=len(lat0),len(lon0)
    
#     loni=np.where(np.logical_and(lon0>=lonbounds[0], lon0<lonbounds[1]))[0]
#     lati=np.where(np.logical_and(lat0>=latbounds[0], lat0<latbounds[1]))[0]
    

#     mask=np.ones((ny,nx))
#     i=0
#     for xx in loni:
#         for yy in lati:
#             mask[yy,xx]=0.

#     return mask


def combinemasked(masked1,masked2):
    # Combine two mutually-exclusive masked arrays. We assume all the masked data are null values so that masked data in one mask does not alterate unmasked data in the second. 
    


    
    if masked1.shape == masked2.shape:
        nj=masked1.shape[0]
        ni=masked1.shape[1]
        if 'mask' in dir(masked1) and 'mask' in dir(masked2):
            mask3=masked1.mask*masked2.mask
            unmasked3=masked1.data+masked2.data
            masked3=np.ma.masked_array(unmasked3,mask=mask3)
            return masked3
        else:
            print 'Mask error.'            
    else:
        print 'Mask error.'
            
            
                
        #data=np.ma.masked_array(data,mask=mask)        
    
# def getlsmask():
#     '''Return numeric land-sea mask with land and sea areas represented by 0 (mask off) and 1 (mask on) respectively'''
    
#     nc=Dataset('/home/leduc/data/CMIP5_1pctCO2/areacello_fx_CanESM2_1pctCO2_r0i0p0.nc')
#     data=nc.variables['areacello'][:].data
#     lon=nc.variables['lon'][:]
#     lat=nc.variables['lat'][:]

#     lon_dest,lat_dest,data=gu.trlonlatdatacmip5(lon,lat,data)
#     #data, lon_dest, lat_dest=gu.interpolateto(data,lon_dest,lat_dest,[1,1])
#     data, lon_dest, lat_dest=gu.interpolateto(data,lon_dest,lat_dest,'CanESM')    


#     mask=np.round(data/np.max(data))
    
#     return mask


def mergemasks(m1,m2):
    '''Combiner deux masques 2D de 0 et de 1. Attention, 0 sont '''
        
    m3=m1+m2
    ny=m3.shape[0]
    nx=m3.shape[1]
    
    for jj in range(ny):
        for ii in range(nx):
            if m3[jj,ii]>0:
                m3[jj,ii]=1


    return m3
        

    
    

def getcellareas():
    nc=Dataset('/dmf2/scenario/external_data/CMIP5/CCCMA/CanESM2/1pctCO2/fx/atmos/r0i0p0/areacella/areacella_fx_CanESM2_1pctCO2_r0i0p0.nc')
    
    data=nc.variables['areacella'][:]
    lon=nc.variables['lon'][:]
    lat=nc.variables['lat'][:]

    lon2,lat2,data2=gu.trlonlatdatacmip5(lon,lat,data)
    
    return data2

def wdacella(data):
    # Return the weighted average over the unmasked regions.

    if len(data.shape)==2:
        data=data[None,:,:]
    
    Nt=data.shape[0]
    Ny0=data.shape[1]
    Nx0=data.shape[2]

    areas=getcellareas()
    Sarea=0.
    tt=0
    pts=[]
    for jj in range(Ny0):
        for ii in range(Nx0):
            if not hasattr(data,'mask') or not data.mask[tt,jj,ii]:
                Sarea+=areas[jj,ii]
                pts.append([jj,ii])

    Sijt=np.zeros(Nt)
    for tt in range(Nt):
        Sij=0.
        for jj,ii in pts:
            Sij=Sij+areas[jj,ii]*data[tt,jj,ii]
                    
        Sijt[tt]=Sij/Sarea

    return Sijt,Sarea


def regionlabpos(reg):
    
    dx,dy=0,0
    if reg in giorgiregions:
        lonb,latb=giorgibounds(reg)
    elif reg in oceanregions:
        lonb,latb=oceanbounds(reg)
    elif reg in mylandregions:
        lonb,latb=myregionsbounds(reg)        
        
    # Giorgi
    if reg=='GRL':
        dx,dy=53,22
    elif reg=='EAS':
        dx,dy=2,23
    elif reg=='SEA':
        dx,dy=8,18
    elif reg=='CNA':
        dx,dy=1,10
    elif reg=='WNA':
        dx,dy=7,16        
    elif reg=='ENA':
        dx,dy=10,10
    elif reg=='AMZ':
        dx,dy=20,5
    elif reg=='SSA':
        dx,dy=8,28
    elif reg=='SAH':
        dx,dy=25,3
    elif reg=='WAF':
        dx,dy=20,20
    elif reg=='EAF':
        dx,dy=5,15
    elif reg=='MED':
        dx,dy=15,5
    elif reg=='NEU':
        dx,dy=30,3
    elif reg=='ALA':
        dx,dy=20,4
    elif reg=='NAS':
        dx,dy=50,9
    elif reg=='CAS':
        dx,dy=15,5
    elif reg=='SAS':
        dx,dy=10,19
    elif reg=='TIB':
        dx,dy=7,10                                                
    elif reg=='AUS':
        dx,dy=12,20
    elif reg=='SAF':
        dx,dy=26,13
        
    # Oceans
    elif reg=='SPO':
        dx,dy=-280,30
    elif reg=='NPO':
        dx,dy=-280,25
    elif reg=='SAO':
        dx,dy=45,30
    elif reg=='NAO':
        dx,dy=50,30
    elif reg=='IO':
        dx,dy=50,30
    elif reg=='AO':
        dx,dy=175,10
    elif reg=='SO':
        dx,dy=130,20

    #Others
    elif reg=='ANT':
        dx,dy=180,8
        
        
    px=lonb[0]+dx
    py=latb[0]+dy

    return px,py

# def regsurfarea(areas):
#     # Return the total area (in m^2) of the unmasked regions.

#     Nt=areas.shape[0]
#     Ny0=areas.shape[1]
#     Nx0=areas.shape[2]

#     areas=getcellareas()
#     Sarea=0.
#     for jj in range(Ny0):
#         for ii in range(Nx0):
#             if not ma.getmask(areas) or not areas.mask[tt,jj,ii]:
#                 Sarea+=areas[jj,ii]

#     Sijt=np.zeros(Nt)
#     for tt in range(Nt):
#         Sij=0.
#         for jj in range(Ny0):
#             for ii in range(Nx0):
#                 if not ma.getmask(areas) or not areas.mask[tt,jj,ii]:
#                     Sij=Sij+areas[jj,ii]*areas[tt,jj,ii]
                    
#         Sijt[tt]=Sij/Sarea

#     return Sijt





    

# def wda(data,lat):
#     '''Weighted domain average with masked data on for regular 3D grid.'''


#     if len(data.shape)==2:
#         sys.exit('Error')


#     elif len(data.shape)==3:
#         Nt=data.shape[0]
#         Ny0=data.shape[1]
#         Nx0=data.shape[2]

#         Sijt=np.zeros(Nt)
#         for tt in range(Nt):
    
#             Sij=0.
#             wjsum=0
#             Ny=0
#             for jj in range(Ny0):
#                 foundonlat=0                
#                 Sj=0.
#                 Nx=0
#                 for ii in range(Nx0):
#                     if not data.mask[tt,jj,ii]:
#                         Sj=Sj+data[tt,jj,ii]
#                         Nx+=1
#                         foundonlat=1
#                 if foundonlat==1:
#                     Ny+=1

#                 #embed()
                
#                 if foundonlat==1:
                
#                     wj=(np.pi/(2.*Nx))*np.cos(lat[jj]*np.pi/180.)
#                     Sij=Sij+wj*Sj
                
#             Sijt[tt]=Sij/Ny
            
#         return Sijt



