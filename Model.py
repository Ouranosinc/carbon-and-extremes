from IPython import embed
import copy
# import os
import sys
from netCDF4 import Dataset
from netCDF4 import num2date
from netCDF4 import date2num
from datetime import datetime
import numpy as np

import timeutils as tu
import gridutils as gu




reload(tu)
reload(gu)


# #from netCDF4 import datetime

# import numpy as np

# import pickle
#import fnmatch

# import mpl_toolkits
# from mpl_toolkits.basemap import Basemap
# import matplotlib as mpl
# import matplotlib.pyplot as plt
# from matplotlib.ticker import MaxNLocator
# from matplotlib.colors import BoundaryNorm
import numpy.ma as ma # for masks

# my modules
#import maputil as mu



############################################################################
# CLASS MODEL
############################################################################

class Model:
    ''' Class for a set of simulations (members) based on the same experiment (ensemble, scenario, period).'''

    def __init__(self,simdic='Dummy'):
        try:
            mod,scen,var,mem=simdic['mod'],simdic['scen'],simdic['var'],simdic['mem']
            dummy=1

            nc=Dataset(simdic['pathpre']+simdic['pathsuf'])

            # Model Identity
            self.name=simdic['mod']

            # Model data structure
            self.data={}
            self.data[scen]={}
            self.data[scen][var]={}
            self.data[scen][var][mem]={}

            # Lat/Lon that characterize the model
            self.lat=nc.variables['lat'][:]
            self.lon=nc.variables['lon'][:]

            if 'time' in nc.variables:
                self.data[scen][var][mem]['mts']={}
                self.data[scen][var][mem]['mts']['series']=[] 

                # Add data
                data=nc.variables[simdic['var']][:,:,:]
                if 'missing_value' in dir(nc.variables[simdic['var']]):
                    data=ma.getdata(data)
                    data[data==nc.variables[simdic['var']].missing_value]=0

                #embed()
                self.data[scen][var][mem]['mts']['series']=data
                self.data[scen][var][mem]['mts']['time']=dTime(nc.variables['time'][:],
                                                              nc.variables['time'].units,
                                                              nc.variables['time'].calendar)

                
            else:
                self.data[scen][var][mem]['fx']={}

                # Add data
                self.data[scen][var][mem]['fx']=nc.variables[simdic['var']][:,:]


            # Init message
            print
            print '++++++++++++ ADDING A NEW MODEL ++++++++++++++++++++++++++++++++++++++'
            print self.name+' model object initialized with '+'('+simdic['scen']+','+simdic['var']+','+simdic['mem']+')'

        except:
            # Dummy model
            print "WARNING: using dummy model template because "+str(sys.exc_info()[1])

            self.name=simdic
            self.data={}

    def AddData(self,simdic):
        '''Return True if model does not exist, and hence can be added. If False, the model should be appended somehow. '''

        scen,var,mem=simdic['scen'],simdic['var'],simdic['mem']
        [modchk,scenchk,varchk,memchk]=self.ModelCheck(simdic)

        print 'modchk,scenchk,varchk,memchk'
        print modchk,scenchk,varchk,memchk
        
        strucloc='('+simdic['mod']+','+simdic['scen']+','+simdic['var']+','+simdic['mem']+')'

        if modchk is False:
            return False
        
        if [modchk,scenchk,varchk,memchk]==[True,True,True,True]:
            print
            print "-Case 1: Appending time series-"

            nc=Dataset(simdic['pathpre']+simdic['pathsuf'])
   
            if 'time' in nc.variables:
                if nc.variables['time'][:].shape == self.data[scen][var][mem]['mts']['time'].array.shape:
                    if (nc.variables['time'][:] == self.data[scen][var][mem]['mts']['time'].array).all():
                        print 'Time series completely overlap on '+strucloc+'. Cannot process data.'
                        return True     # Not sure of this case !!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                # Add data
                print "Adding data on "+strucloc
                data=nc.variables[simdic['var']][:,:,:]
                if 'missing_value' in dir(nc.variables[simdic['var']]):
                    data=ma.getdata(data)
                    data[data==nc.variables[simdic['var']].missing_value]=0
                self.data[scen][var][mem]['mts']['series']=np.append(self.data[scen][var][mem]['mts']['series'],
                                                                     data,axis=0)
                self.data[scen][var][mem]['mts']['time'].array=                np.append(self.data[scen][var][mem]['mts']['time'].array, nc.variables['time'][:])

            else:
                print "Adding data on "+strucloc
                self.data[scen][var][mem]['fx']=np.append(self.data[scen][var][mem]['fx'],nc.variables[simdic['var']],axis=0)
            return True
        
        elif [modchk,scenchk,varchk,memchk]==[True,True,True,False]:
            print
            print "-Case 2-"

            nc=Dataset(simdic['pathpre']+simdic['pathsuf'])
            
            # Model data structure
            self.data[scen][var][mem]={}

            if 'time' in nc.variables:
                self.data[scen][var][mem]['mts']={}
                self.data[scen][var][mem]['mts']['series']=[] 
                self.data[scen][var][mem]['mts']['time']=[]

                # Add data
                print "Adding member at "+strucloc
                data=nc.variables[simdic['var']][:,:,:]
                if 'missing_value' in dir(nc.variables[simdic['var']]):
                    data=ma.getdata(data)
                    data[data==nc.variables[simdic['var']].missing_value]=0
                self.data[scen][var][mem]['mts']['series']=data
                self.data[scen][var][mem]['mts']['time']=dTime(nc.variables['time'][:],
                                                              nc.variables['time'].units,
                                                              nc.variables['time'].calendar)

            else:
                self.data[scen][var][mem]['fx']={}

                # Add data
                print "Adding member on "+strucloc
                self.data[scen][var][mem]['fx']= nc.variables[simdic['var']][:]
                
            return True
        
        elif [modchk,scenchk,varchk,memchk]==[True,True,False,False]:
            print
            print "-Case 3-"
            print "Adding variable at "+strucloc

            nc=Dataset(simdic['pathpre']+simdic['pathsuf'])

            
            # Model data structure
            self.data[scen][var]={}
            self.data[scen][var][mem]={}
            
            if 'time' in nc.variables:            
                self.data[scen][var][mem]['mts']={}
                self.data[scen][var][mem]['mts']['series']=[] 

                # Add data
                data=nc.variables[simdic['var']][:,:,:]
                if 'missing_value' in dir(nc.variables[simdic['var']]):
                    data=ma.getdata(data)                    
                    data[data==nc.variables[simdic['var']].missing_value]=0
                self.data[scen][var][mem]['mts']['series']=data                
                self.data[scen][var][mem]['mts']['time']=dTime(nc.variables['time'][:],
                                                              nc.variables['time'].units,
                                                              nc.variables['time'].calendar)
            else:
                self.data[scen][var][mem]['fx']={}

                # Add data
                self.data[scen][var][mem]['fx'] = nc.variables[simdic['var']][:]
                
            return True
        
        elif [modchk,scenchk,varchk,memchk]==[True,False,False,False]:
            print
            print "---------- Case 4 ----------"            
            print "Adding scenario at "+strucloc

            nc=Dataset(simdic['pathpre']+simdic['pathsuf'])
            
            # Model data structure
            self.data[scen]={}
            self.data[scen][var]={}
            self.data[scen][var][mem]={}

            if 'time' in nc.variables:            
                self.data[scen][var][mem]['mts']={}
                self.data[scen][var][mem]['mts']['series']=[] 

                # Add data
                data=nc.variables[simdic['var']][:,:,:]
                if 'missing_value' in dir(nc.variables[simdic['var']]):
                    data=ma.getdata(data)                    
                    data[data==nc.variables[simdic['var']].missing_value]=0
                self.data[scen][var][mem]['mts']['series']=data                
                self.data[scen][var][mem]['mts']['time']=dTime(nc.variables['time'][:],
                                                              nc.variables['time'].units,
                                                              nc.variables['time'].calendar)

            else:
                self.data[scen][var][mem]['fx']={}

                # Add data
                self.data[scen][var][mem]['fx'] = nc.variables[simdic['var']][:]

                
            return True            
        
        elif [modchk,scenchk,varchk,memchk]==[False,False,False,False]:
            print
            print "++++++++++ Case 5 (NOT IMPLEMENTED YET!) ++++++++++"            
            print 'Models'' differ. Whether try with another model object or create a new one.'
            sys.exit()
        else:
            print [modchk,scenchk,varchk,memchk]
            sys.exit('Unexpected case at '+strucloc)
                
        
    def AggSeasons(self,repair='yes', seasons=['ANN','DJF','MAM','JJA','SON']):
        '''Aggregation temporelle de series mensuelles a moyennes saisonnieres et annuelles.'''

        lon=self.lon
        lat=self.lat
        scens=self.data.keys()
        
        for scen in scens:
            vrs=self.data[scen].keys()
            for var in vrs:

                mms=self.data[scen][var].keys()
                mms.sort()

                
                for mem in mms:
                    if 'mts' in self.data[scen][var][mem]:
                        for sea in seasons:
                            self.data[scen][var][mem][sea]={}
                            self.data[scen][var][mem][sea]['series']=tu.tsmonths2seas(self.data[scen][var][mem]['mts']['series'],sea)
                            self.data[scen][var][mem][sea]['time']=yTime(self.data[scen][var][mem]['mts']['time'].year0+
                                                                         np.arange(len(self.data[scen][var][mem][sea]['series'])),
                                                                        'Years',self.data[scen][var][mem]['mts']['time'].calendar,
                                                                        self.data[scen][var][mem]['mts']['time'].ndy)
                            if repair=='yes':
                                data=self.data[scen][var][mem][sea]['series']
                                lon2,lat2,data2=gu.trlonlatdatacmip5(lon,lat,data)
                                self.data[scen][var][mem][sea]['series']=data2

                        self.data[scen][var][mem].pop('mts')

                    elif 'fx' in self.data[scen][var][mem]:
                        if repair=='yes':
                            data=self.data[scen][var][mem]['fx']
                            lon2,lat2,data2=gu.trlonlatdatacmip5(lon,lat,data)
                            self.data[scen][var][mem]['fx']=data2

                        
        if repair=='yes':                   
            self.lon=lon2
            self.lat=lat2
                                    
        return


    
    def Interpolate(self,destgrid,seasons):
        '''Interpolate data'''
        
        #Xres=xyres[0]
        #Yres=xyres[1]
        scens=self.data.keys()
        for scen in scens:
            vrs=self.data[scen].keys()
            for var in vrs:
                mms=self.data[scen][var].keys()
                mms.sort()
                for mem in mms:
                    if 'fx' not in self.data[scen][var][mem]:
                        for sea in seasons:
                            data=self.data[scen][var][mem][sea]['series']
                            #result,lon_dest,lat_dest=interpcustglob(data,self.lon,self.lat,Xres,Yres)
                            result,lon_dest,lat_dest=gu.interpolateto(data,self.lon,self.lat,destgrid)
                            self.data[scen][var][mem][sea]['series']=result
                            
                    elif 'fx' in self.data[scen][var][mem]:
                            data=self.data[scen][var][mem]['fx']
                            #result,lon_dest,lat_dest=interpcustglob(data,self.lon,self.lat,Xres,Yres)
                            result,lon_dest,lat_dest=gu.interpolateto(data,self.lon,self.lat,destgrid)                            
                            self.data[scen][var][mem]['fx']=result
                        
        self.lon=lon_dest
        self.lat=lat_dest

        return

    # def Mmavg(self,scen,var,sea,clim):
    #     ''' Average over members and return a matrix.'''

    #     y0,y1=ComPer([self])
    #     if clim[0]<y0:
    #         sys.exit('Start year out of bounds.')
    #     elif clim[1]>y1:
    #         sys.exit('End year out of bounds.')

    #     mems=self.Mems(scen,var)    
    #     Nmems=len(mems)

    #     mmavg=self.Get(scen,var,mems[0],sea,clim)
    #     for mem in mems[1:]:
    #         mat=self.Get(scen,var,mem,sea,clim)
    #         mmavg+=mat

    #     return mmavg/Nmems


    # def Mmstd(self,scen,var,sea,clim):
    #     ''' Inter-member spread calculated as the square root of the variance with N-1 degrees of freedom.'''

    #     y0,y1=ComPer([self])
    #     if clim[0]<y0:
    #         sys.exit('Start year out of bounds.')
    #     elif clim[1]>y1:
    #         sys.exit('End year out of bounds.')

    #     mems=self.Mems(scen,var)    
    #     Nmems=len(mems)

    #     mmavg=self.Mmavg(scen,var,sea,clim)

    #     mmsst=(self.Get(scen,var,mems[0],sea,clim)-mmavg)**2
    #     for mem in mems[1:]:
    #         mmsst+=(self.Get(scen,var,mem,sea,clim)-mmavg)**2

    #     return np.sqrt(mmsst/(Nmems-1.))

    

    def ModelCheck(self,simdic):
        '''Compare current Model object to simdic, a model entry to be added. For example, if modchk is True but scenchk, varchk and memchk are False, this means that we should create new scenario entry for that specific model. Only if everything is True one must append the time series.'''

        modchk=False
        scenchk=False
        varchk=False
        memchk=False


        if self.name == simdic['mod']: 
            modchk=True

            if simdic['scen'] in self.data.keys():
                scenchk=True

                if simdic['var'] in self.data[simdic['scen']].keys():
                    varchk=True

                    if simdic['mem'] in self.data[simdic['scen']][simdic['var']].keys():
                        memchk=True

        
        return [modchk,scenchk,varchk,memchk]


    def Get(self,scen,var,mem,sea,clim=None,typ='series'):
        '''Extracting a branch of the data tree in a Model object. If clim[0] and clim[1] are -1, the entire time series is extracted with dt.'''

        tts=self.data[scen][var][mem][sea]['time'].array
        data=self.data[scen][var][mem][sea][typ]

        if var is 'tas':
            data=data-273.15
        elif var is 'pr':
            data=data*86400

        if clim is None:
            y0=tts[0]
            y1=tts[-1]
            dt=1            
        else:
            y0=clim[0]
            y1=clim[1]                
            dt=clim[2]

        tts2,data2=tu.tsyear2clim(tts,data,y0,y1,dt)

        return {'time':tts2,typ:data2}


    def Scens(self):
        return self.data.keys()

    def Vars(self,scen):
        return self.data[scen].keys()

    
    def Mems(self,scen,var):
        mms= self.data[scen][var].keys()
        mms.sort()
        return mms

    def Seas(self,scen,var,mem):
        tagg=self.data[scen][var][mem].keys()
        seas=[sea for sea in tagg if sea in ['ANN','DJF','MAM','JJA','SON','mts']]
        others=[sea for sea in tagg if sea not in ['ANN','DJF','MAM','JJA','SON','mts']]
        
        return seas,others
        
    
    def Nmem(self,scen,var):
        return float(len(self.data[scen][var]))
        

    def Show(self):
        print ''
        print 'Model: ', self.name

        scens=self.data.keys()
        for scen in scens:
            vrs=self.data[scen].keys()
            for var in vrs:
                mms=self.data[scen][var].keys()
                for mm in mms:
                    tagg=self.data[scen][var][mm].keys()
                    seas=[sea for sea in tagg if sea in ['ANN','DJF','MAM','JJA','SON','mts']]
                    others=[sea for sea in tagg if sea not in ['ANN','DJF','MAM','JJA','SON','mts']]
                    
                    for sea in seas:
                        if 'series' in self.data[scen][var][mm][sea]:
                            Nt,Ny,Nx=self.data[scen][var][mm][sea]['series'].shape
                            time=self.data[scen][var][mm][sea]['time'].array
                            y0,y1=time[0],time[-1]
                            y0y1='-'.join([str(y0),str(y1)])
                            print '('+scen+', '+var+', '+mm+', '+sea+', [Nt,Ny,Nx = '+str(Nt)+','+str(Ny)+','+str(Nx)+'], '+y0y1+')'

                        elif 'global' in self.data[scen][var][mm][sea]:
                            Nt=self.data[scen][var][mm][sea]['global'].shape
                            print '('+scen+', '+var+', '+mm+', global, [Nt = '+str(Nt)+'])'
                        
                    for other in others:
                        if other == 'fx':
                            Ny,Nx=self.data[scen][var][mm][other].shape
                            print '('+scen+', '+var+', '+mm+', fx, [Ny,Nx = '+str(Ny)+','+str(Nx)+'])'

                            
        return
    


    def Resolution(self):

        lon=self.lon
        lat=self.lat
        nx=lon.shape[0]
        ny=lat.shape[0]
                
        resx=np.zeros(nx-1)
        resy=np.zeros(ny-1)


        for i in np.arange(nx-1):
            resx[i]=lon[i+1]-lon[i]
        for i in np.arange(ny-1):
            resy[i]=lat[i+1]-lat[i]
            
        return [np.mean(resx),np.mean(resy)]

    def Touch(self,scen,var,mem,sea):
        try:
            if sea in self.data[scen][var][mem]:
                return True
            else:
                sys.exit('Entry'+'-'.join([self.name,scen,var,mem,sea])+' exists but no such season.')
                return False
        except:
            #print 'Error: Entry '+'-'.join([self.name,scen,var,mem,sea])+' does not exist.'
            return False


    def Add2Dic(self, subtree, scen='', var='', mem='', sea='', typ=''):
        try:
            #print 'Try type level.'
            self.data[scen][var][mem][sea][typ]=subtree
        except:
            try:
                #print 'Try season level.'
                self.data[scen][var][mem][sea]={}
                self.data[scen][var][mem][sea][typ]=subtree
            except:
                try:
                    #print 'Try member level.'
                    self.data[scen][var][mem]={}
                    self.data[scen][var][mem][sea]={}
                    self.data[scen][var][mem][sea][typ]=subtree                              
                except:
                    try:
                        #print 'Try variable level.'                                    
                        self.data[scen][var]={}
                        self.data[scen][var][mem]={}
                        self.data[scen][var][mem][sea]={}
                        self.data[scen][var][mem][sea][typ]=subtree
                    except:
                        try:
                            #print 'Adding at type level.'
                            self.data[scen]={}
                            self.data[scen][var]={}
                            self.data[scen][var][mem]={}
                            self.data[scen][var][mem][sea]={}
                            self.data[scen][var][mem][sea][typ]=subtree
                            
                        except:
                            sys.error('Unexpected error.')

    def Map(self):
        '''Map structure of the model object.'''

        print 'Mapping of '+self.name+' object.'

        scens=self.data.keys()
        for scen in scens:
            print '_'+scen
            vrs=self.data[scen].keys()
            for var in vrs:
                print ' \__'+var
                mems=self.data[scen][var].keys()
                for mem in mems:
                    print '  \___'+mem
                    seas=self.data[scen][var][mem].keys()
                    for sea in seas:
                        print '   \____'+sea
                        try:
                            typs=self.data[scen][var][mem][sea].keys()
                            for typ in typs:
                                print '    \________'+typ
                        except:
                            pass
    
############################################################################
# CLASS MME
############################################################################
        
class MME:
    ''' Class MME (multi-model ensemble). This is basically a list of
    Model objects (self.models) and the following methods.'''

    def __init__(self,description,simdb=[]):
        self.description=description
        self.models=[]

        for simdic in simdb:   #Sims to add
            added=False
            
            for Mod in self.models:           #Try to add to known models
                print ">>>>>>>>>>>>>>>"
                print "Try to add "+simdic['pathsuf'].split('/')[-1]+" to "+Mod.name
                added=Mod.AddData(simdic)

                if added is True:
                    break

            if added is False:                #Append a new model object.
                print "Appending new model "+simdic['mod']
                self.models.append(Model(simdic))

    def AddModel(self,mod):
        '''Add a model object without any testing. Will replace if already exists.'''
        self.models.append(mod)

        
    def Models(self):
        '''Return the list of model namestrings.'''

        mods=[]
        for mod in self.models:
            mods.append(mod.name)

        return mods
                
    def AggSeasons(self,repair='yes', seasons=['ANN','DJF','MAM','JJA','SON']):
        for mod in self.models:
            mod.AggSeasons(repair=repair,seasons=seasons)

    def Mod(self,name):
        '''Return model object from its namestring.'''
        return [mod for mod in self.models if mod.name==name][0]
        
        
    def Interpolate(self,xyres=None,seasons=['ANN','DJF','MAM','JJA','SON']):
        #
        for mod in self.models:
            mod.Interpolate(xyres,seasons)


    # def Mavg(self,scen,var,sea,clim,models=[]):
    #     '''Average over models, each model being member-averaged.'''

    #     # All models (default) or selection
    #     try:
    #         models[0]
    #     except:
    #         models=self.Models()

    #     y0,y1=ComPer(self.models) 
    #     if clim[0]<y0:
    #         sys.exit('Start year out of bounds.')
    #     elif clim[1]>y1:
    #         sys.exit('End year out of bounds.')

    #     Nmod=self.Nmod()

    #     mavg=self.Mod(models[0]).Mmavg(scen,var,sea,clim)
    #     for mo in models[1:]:
    #         mod=self.Mod(mo)
    #         mavg+=mod.Mmavg(scen,var,sea,clim)

    #     return mavg/Nmod



    # def Nmod(self):
    #     return float(len(self.models))
            
            
    def Resolution(self):
        
        form1="%5s %18s %14s"
        form2="%5d %18s %14s"        

        # print
        # print '------------------------------------'
        # print form1 % ('#','Model','Resolution')
        # print '------------------------------------'


        
        i=0
        for mod in self.models:
            rx,ry=mod.Resolution()
            res= "%4.2fx%4.2f" % (rx,ry)
            
            print form2 % (i,mod.name,res)
            i+=1

            
    def Show(self):
        
        for mod in self.models:
            mod.Show()


    def Show2(self):

        print
        form1="%15s %10s %10s %8s"
        print form1 % ("Name","Scen","Var","Run")
        print form1 % ("---------------","----------","----------","--------")

        for mod in self.models:
            scens=mod.data.keys()
            for scen in scens:
                vrs=mod.data[scen].keys()
                for var in vrs:
                    mms=mod.data[scen][var].keys()
                    for mm in mms:
                        print form1 % (mod.name,scen,var,mm)

        
    def MapMME(self):
        for mod in self.models:
            mod.Map()
            

    def Touch(self,modelname,scen,var,mem,sea):
        return self.Mod(modelname).Touch(scen,var,mem,sea)
            

################################################################################
# class TIME
################################################################################

class dTime():
    def __init__(self,array,units,calendar):
        self.array=array
        self.units=units
        self.calendar=calendar

        if units=='days since 0000-01-01 00:00:00':
            units='days since 0001-01-01 00:00:00'
            print 'Calendar Warning: There is no year 0 in the Gregorian or Julian calendars.'
        self.year0=num2date(array[0],units,calendar).year
        
        self.ndy=date2num(datetime(2001,1,1),units,calendar)-date2num(datetime(2000,1,1),units,calendar)

class yTime():
    def __init__(self,array,units,calendar,ndy):
        self.array=array
        self.units=units
        self.calendar=calendar
        self.ndy=ndy
        


################################################################################
# Global operations on objects
################################################################################

def AppScen(mme1,scen1,mme2,scen2):
    '''Append MME objects along the scenarios axis with (mme1,scen1) and (mme2,scen2) being the historical period and futur scenarios respectively.
    Overwrite common time steps in the historical period. Effectue une copie de (2) et va chercher ce qui manque dans (1).'''

    print ''
    print '++++++++++++++++ APPENDING SCENARIOS: '+scen1+'->'+scen2+' +++++++++++++++++++++++++++++++'
    
    # Copy destination object
    mme_dest=copy.deepcopy(mme2)

    for mod in mme2.models:
        vrs=mod.Vars(scen2)
        for var in vrs:
            mems=mod.Mems(scen2,var)
            for mem in mems:
                seas,others=mod.Seas(scen2,var,mem)
                for sea in seas:
                    strucloc='('+mod.name+','+var+','+mem+sea+')'                    
                    if mme1.Touch(mod.name,scen1,var,mem,sea):   # Find historical component
                        
                        print '>>>>>>>>>>>>>>>>>>',mod.name,var,mem,sea
                        # Overlap, consecutive, or subsequent but non-continuous
                        t1=mme1.Mod(mod.name).data[scen1][var][mem][sea]['time'].array
                        t2=mod.data[scen2][var][mem][sea]['time'].array

                        s1=t1[0]          # First year scen 1
                        e1=t1[-1]         # Last year scen 1
                        s2=t2[0]
                        e2=t2[-1]

                        if (s1>=s2):
                            sys.error(strucloc+'--CASE 0: S1 start at the same year or after S2. Try to invert the order.')
                        else:             # (s1<s2)
                            if (e2<=e1):
                                sys.error('--CASE 1: S2 is useless, starting after and ending before S1.')
                            if (s2<=e1) or (s2==e1+1):
                                if (s2<=e1):
                                    print strucloc+'--CASE 2: Overlapping series... will overwrite S1 data for common period.'
                                    s2bi=np.where(t1==s2)[0][0]   # Index of where S2 starts in t1.
                                    mme_dest.Mod(mod.name).data[scen2][var][mem][sea]['time'].array=np.append(mme1.Mod(mod.name).data[scen1][var][mem][sea]['time'].array[0:s2bi],
                                                                                                              mod.data[scen2][var][mem][sea]['time'].array,0)
                                    mme_dest.Mod(mod.name).data[scen2][var][mem][sea]['series']=np.append(mme1.Mod(mod.name).data[scen1][var][mem][sea]['series'][0:s2bi],
                                                                                                          mod.data[scen2][var][mem][sea]['series'],0)   
                                elif (s2==e1+1):
                                    print strucloc+'--CASE 3: Data are continuous. Scenarios can be appended perfectly.'
                                    mme_dest.Mod(mod.name).data[scen2][var][mem][sea]['time'].array=np.append(mme1.Mod(mod.name).data[scen1][var][mem][sea]['time'].array,
                                                                                                              mod.data[scen2][var][mem][sea]['time'].array,0)
                                    mme_dest.Mod(mod.name).data[scen2][var][mem][sea]['series']=np.append(mme1.Mod(mod.name).data[scen1][var][mem][sea]['series'],
                                                                                                          mod.data[scen2][var][mem][sea]['series'],0)   

                            else:
                                print s1,e1,s2,e2
                                sys.error('--CASE 4: Non continuous data. We will append but then fill the holes with NAN.')

                    else:
                        print '----'
                        print mod.name
                        print scen1
                        print var
                        print mem
                        print sea
                        print '----'                        
                        sys.exit('Error, historical component not found for ('+'-'.join([mod.name,scen1,var,mem,sea])+')')
                        
    return mme_dest


def ComPer(models):
    '''Find the common time period from a list of model objects.'''
    
    y0=[]
    y1=[]
            
    for mod in models:
        scens=mod.data.keys()
        for scen in scens:
            vrs=mod.data[scen].keys()
            for var in vrs:
                mms=mod.data[scen][var].keys()
                for mm in mms:
                    seas=mod.data[scen][var][mm].keys()
                    for sea in seas:
                        time=mod.data[scen][var][mm][sea]['time'].array
                        y0.append(time[0]), y1.append(time[-1])
                        
    y0=list(set(y0))
    y1=list(set(y1))
    return max(y0),min(y1)



            
    
