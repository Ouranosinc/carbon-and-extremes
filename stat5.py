import numpy as np
from IPython import embed



def ergovar(data,pdeg,x=None):
    '''Calculate the temporal variability of a 2-D field, also known as ergodic variance.'''
    
    try: Nt,Ny,Nx=data.shape
    except: Nt,=data.shape        
        
    
    # 1) Detrending
    data2=detrend(data,pdeg,x=x)
    sse=np.squeeze(sum(data2**2,0))
    

    # 3) calculate variance

    tvar=sse/(Nt-pdeg-1)
    #print np.sqrt(tvar[4,4])
    #print np.sqrt(sse[4,4]/(Nmem*Nt))
    
    return tvar



def detrend(data,pdeg,x=None, coefs=0):
    '''Detrend 2D fields or 1D time series using a pdeg-degree polynomial.'''

## debugging
#                                      # 2-D
#    Nt,Ny,Nx=data.shape
#    data2=np.zeros((Nt,Ny,Nx))
#    cs=np.zeros((pdeg+1,Ny,Nx))
#    if x==None: x=np.arange(Nt)
#        
#
#    for xx in np.arange(Nx):
#        for yy in np.arange(Ny):
##            if xx==67 and yy==36:
##                print xx,yy
#            cs[:,yy,xx]=np.polyfit(x,data[:,yy,xx],pdeg)
#            pol=np.poly1d(cs[:,yy,xx])
#            yhat=pol(x)
#            data2[:,yy,xx]=data[:,yy,xx]-yhat
#
#    
#
#    if coefs==1:
#        return data2,cs
#    else:
#        return data2
# debuggin ends

    try:                                  # 2-D
        Nt,Ny,Nx=data.shape
        data2=np.zeros((Nt,Ny,Nx))
        cs=np.zeros((pdeg+1,Ny,Nx))
        if x==None: x=np.arange(Nt)
            

        for xx in np.arange(Nx):
            for yy in np.arange(Ny):
                cs[:,yy,xx]=np.polyfit(x,data[:,yy,xx],pdeg)
                pol=np.poly1d(cs[:,yy,xx])
                yhat=pol(x)
                data2[:,yy,xx]=data[:,yy,xx]-yhat

    except:                               # 1-D
        print data.shape        
        Nt,=data.shape
        data2=np.zeros(Nt)
        if x==None: x=np.arange(Nt)

        cs=np.polyfit(x,data,pdeg)
        pol=np.poly1d(cs)
        yhat=pol(x)
        data2=data-yhat

    if coefs==1:
        return data2,cs
    else:
        return data2

    
def SSEpoly(data,pdeg,x=None,coefs=0):
    '''Calculate SSE around a pdeg-degree polynomial fit. Return SSE (1D or 2D) and the df.'''

    try:    nt,ny,nx=data.shape
    except: nt,=data.shape

    if x==None: x=np.arange(nt)
        
    xdet,cs=detrend(data,pdeg,x=x,coefs=1)
    sse=np.sum(xdet**2,axis=0)
    df=nt-pdeg-1

    if coefs==1:
        return sse,float(df),cs        
    else:
        return sse,float(df)
    


    
def det3d(data,pdeg,x=None):
    '''Detrend 2D fields using a pdeg-degree polynomial.'''

    Nt,Ny,Nx=data.shape
    if x==None: x=np.arange(Nt)
        
    data2=np.zeros((Nt,Ny,Nx))
    #embed()
    for xx in np.arange(Nx):
        for yy in np.arange(Ny):
            cs=np.polyfit(x,data[:,yy,xx],pdeg)
            pol=np.poly1d(cs)
            yhat=pol(x)
            data2[:,yy,xx]=data[:,yy,xx]-yhat

    return data2



def autocorr2d(data,lag):
    '''Autocorrelation in time for 2-D fields.'''
    nt,ny,nx=data.shape
    ac2d=np.zeros((ny,nx))

    for jj in np.arange(ny):
        for ii in np.arange(nx):
            ac2d[jj,ii]=autocorr(data[:,jj,ii],1)
            
    return ac2d
    
    

def autocorr(z,lag=0):
    '''Calculate autocorrelation for a 1-D array. Give the aucocorellation for all lags if lag is not given.'''
    n=z.shape[0]
    
    if lag==0:
        ac=np.zeros(n)
        for lag in np.arange(n):
            x=z[lag:]
            y=z[0:-lag]
            if lag==0: y=x

            ac[lag]=np.corrcoef(x,y)[0,1]
    else:
        x=z[lag:]
        y=z[0:-lag]
        ac=np.corrcoef(x,y)[0,1]        
    return ac

def tagg(x,dt):
    '''Aggregate (average) a 1-D array with a window of length dt.'''

    dt=int(dt)    
    nx=x.shape[0]
    ny=nx/dt

    yp=np.zeros(ny)

    for jj in np.arange(ny):
        y[jj]=np.mean(x[dt*jj:dt*(jj+1)])
    
    return y


