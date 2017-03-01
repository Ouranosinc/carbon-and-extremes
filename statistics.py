import numpy as np
############################################################################
# SPATIAL STATISTICS (on 2D-GRID)
############################################################################

def wda(data,lat):
    '''Weighted domain average for regular 2D or 3D grid'''


    if len(data.shape)==2:
        Ny=data.shape[0]
        Nx=data.shape[1]

    
        Sij=0.
        wjsum=0
        for jj in range(0,Ny):
            Sj=0.
            for ii in range(0,Nx):
                Sj=Sj+data[jj][ii]
            
            wj=(np.pi/(2.*Nx))*np.cos(lat[jj]*np.pi/180.)
            Sij=Sij+wj*Sj

        return Sij/Ny


    elif len(data.shape)==3:
        Nt=data.shape[0]
        Ny=data.shape[1]
        Nx=data.shape[2]

        Sijt=np.zeros(Nt)
        for tt in range(Nt):
    
            Sij=0.
            wjsum=0
            for jj in range(Ny):
                Sj=0.
                for ii in range(Nx):
                    Sj=Sj+data[tt][jj][ii]
            
                wj=(np.pi/(2.*Nx))*np.cos(lat[jj]*np.pi/180.)
                Sij=Sij+wj*Sj


            Sijt[tt]=Sij/Ny
            
        return Sijt
        
