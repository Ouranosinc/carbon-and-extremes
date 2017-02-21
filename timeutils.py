from IPython import embed
import numpy as np
import sys
#########################################################################
# EXTERNAL FUNCTIONS


def tsmonths2seas(mat,sea):
    '''Filter a 3d matrix over monthly series to obtain seasonal and annual averages.

    It assumes the monthly series to start from January.'''

    Nt,Ny,Nx=mat.shape
    if Nt % 12 >0 :
        Nt2= Nt - Nt % 12
        Nt=Nt2
        
    Nyear=Nt/12

    if sea is 'DJF':
        monthsel=[0,1]

        mat2=np.zeros((Nyear,Ny,Nx))
        mat2[0,:,:]=np.mean(mat[monthsel,:,:],0)
        
        monthsel=[-1,0,1]
        for year in np.arange(1,Nyear):
            mat2[year,:,:]=np.mean(mat[year*12+monthsel,:,:],0)        
    else:
        if sea is 'JJA':
            monthsel=[5,6,7]
        elif sea is 'SON':
            monthsel=[8,9,10]
        elif sea is 'MAM':
            monthsel=[2,3,4]                        
        elif sea is 'ANN':
            monthsel=[0,1,2,3,4,5,6,7,8,9,10,11]
        
        mat2=np.zeros((Nyear,Ny,Nx))
        for year in np.arange(0,Nyear):
            mat2[year,:,:]=np.mean(mat[year*12+monthsel,:,:],0)

    return mat2


def tsyear2clim(tts,data,y0,y1,dt):
    '''Transform a yearly time series into a climatological (dt in year) time series.'''

    y0i=np.where(tts==y0)[0][0]

    try:
        y1i=np.where(tts==y1)[0][0]
    except:
        print "Last year is "+str(tts[-1])+' but we need '+str(y1)
        print y0,y1,dt
        if y1-tts[-1] < 5:
            print "We will patch the missing years with the last existing one."
            print
            nt,ny,nx=data.shape
            #data=np.append(data,np.zeros((y1-tts[-1],ny,nx)),axis=0)


            patch=np.zeros((y1-tts[-1],ny,nx))+data[-1]
            data=np.append(data,patch,axis=0)

            tts=np.append(tts,np.arange(tts[-1]+1,y1+1))
            y1i=np.where(tts==y1)[0][0]            
            
        else:
            sys.exit("Too many time steps are missing at the end of the time series.")


    # Extract the period
    tts2=tts[y0i:y1i+1]
    data2=data[y0i:y1i+1]

    if dt==1:
        return tts2,data2
    else:
        shift=1./2

    if (y1i+1 - y0i)%dt == 0:              # Check for integer num. of dt
        ndt=(y1i+1 - y0i)/dt
        ny,nx=data2.shape[1],data2.shape[2]
        
        tts3=np.zeros(ndt)
        data3=np.zeros((ndt,ny,nx))

        for pp in range(ndt):
            tts3[pp]=y0+(pp+shift)*dt
            data3[pp]=np.mean(data2[pp*dt:(pp+1)*dt],0)
            # data2[pp]=np.mean(data[range(pp*dt,(pp+1)*dt)],0)            

        return tts3,data3
        #return 0,0
    
    else:
        sys.exit('Uneven number of time windows with period range.')
