'''Tools to fetch into a database of netcdf files.'''
import os
import numpy as np
import fnmatch

###############
def ncdbsearch(datadir,infotpl='cmip5file',scenarios=[],realms=[],tres=[],variables=[],models=[],members=[]):
    '''Function that searches recursively in a path (datadir) to generate a database (dictionary) of simulations stored as nc files archived in a CMIP-like structure. '''

    # paths pour tous les fichiers netcdfs
    paths=findncfiles(datadir)

    # Prefixe et suffixe pour chq champs ds path (ou file)
    if infotpl=='cmip5file':
        modpref='_'
        modsuf='_'
        scenpref='_'
        scensuf='_'
        varpref=''
        varsuf='_'
        mempref='_'
        memsuf='_'
        realmpref='_'             #Pas teste
        realmsuf='_'
        # trespref=''
        # tressuf=''                        
    elif infotpl=='cmip3path':
        modpref='/'
        modsuf='/'
        scenpref='/'
        scensuf='/'
        varpref='/'
        varsuf='/'
        mempref='/'
        memsuf='/'
        realmpref='/'
        realmsuf='/'
        trespref='/'
        tressuf='/'                
        
    # selection des simulations en fonction de criteres dans le paths
    if len(scenarios)>0:
        paths=[paths[i] for i in np.arange(len(paths)) for kw in scenarios
               if scenpref+kw.lower()+scensuf in paths[i].lower()]
    if len(realms)>0:
        paths=[paths[i] for i in np.arange(len(paths)) for kw in realms
               if realmpref+kw.lower()+realmsuf in paths[i].lower()]
    if len(tres)>0:
        paths=[paths[i] for i in np.arange(len(paths)) for kw in tres
               if trespref+kw.lower()+tressuf in paths[i].lower()]                
    if len(models)>0:
        paths=[paths[i] for i in np.arange(len(paths)) for kw in models
               if modpref+kw.lower()+modsuf in paths[i].lower()]
    if len(variables)>0:
        paths=[paths[i] for i in np.arange(len(paths)) for kw in variables
               if varpref+kw.lower()+varsuf in paths[i].lower()]
    if len(members)>0:
        paths=[paths[i] for i in np.arange(len(paths)) for kw in members
               if mempref+kw.lower()+memsuf in paths[i].lower()]

    
    paths.sort()


    i=0
    simdb=[]
    for path in paths:
        pathpre=datadir
        pathsuf=path.split(datadir)[1]

        if infotpl=='cmip5file':
            var,mod,scen,mem,tstamp=cmip5filestrinfo(pathsuf)
        elif infotpl=='cmip3path':
            scen,realm,tres,var,mod,mem,tstamp=cmip3pathstrinfo(pathsuf)

        #print path
        #print '%5d | %8s | %17s | %8s | %8s |' % (i,scen,mod,var,mem)

        simdb.append({'id':i,'mod':mod,'scen':scen,'var':var,'mem':mem,'pathpre':pathpre,'pathsuf':pathsuf})

        i+=1

    printdb(simdb)

    
    return simdb

####
def simdbrejecttslice(simdb,yyyymm=210001):
    "Filter a simdb (output from ncdbsearch function) by rejecting time slice beginning at yyyymm or later. Tested for CMIP5 only."
    #filter RCP extension
    simdbnew=[]
    for ii in range(len(simdb)):
        if int(simdb[ii]['pathsuf'].split('/')[-1].split('_')[-1].split('-')[0]) < yyyymm:
            simdbnew.append(simdb[ii])
        
    return simdbnew

###################    
def printdb(simdb):
    ''' Nice display of ncdbsearch output.'''

    print
    print "%3s %14s %10s %7s %8s %60s" % ('id','mod','scen','var','mem','file')
    print '----------------------------------------------------------------------------------------------------------------'
    for entry in simdb:
        print "%3s %17s %10s %7s %8s %60s" % (entry['id'],entry['mod'],entry['scen'],entry['var'],entry['mem'],os.path.basename(entry['pathsuf']))
        #print "%3s" % (entry['id'])


################
def findncfiles(path,fstrmatch=''):
    '''Recursively find all .nc files in a path.'''

    fstrmatch=fstrmatch+'*.nc'
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, fstrmatch):
            if os.stat(os.path.join(root, filename))[6] != 0:
                matches.append(os.path.join(root, filename))
                
    return matches


#####################
def cmip5filestrinfo(string):
    '''Extract info from nc file name in the CMIP5 format such as:
    tas_Amon_MIROC-ESM_1pctCO2_r1i1p1_000101-014012.nc

    Can be given as a path but only basename is considered.
    
    Use:
    var,mod,scen,mem,tstamp=cmip5filestringinfo(string)'''

    fname=os.path.basename(string)
    try:
        var,tmp,mod,scen,mem,tstamp=fname.split('.')[0].split('_')
    except:
        var,tmp,mod,scen,mem=fname.split('.')[0].split('_')
        tstamp='???'
    
    return var,mod,scen,mem,tstamp


def cmip3pathstrinfo(string):
    '''Extract info from path, which needs to begin from the scenario level,
    e.g  sresa1b/atm/mo/tas/ukmo_hadcm3/run1/tas_A1.nc'''
    
    scen,realm,tres,var,mod,mem,base=string.split('/')
    tstamp=''
    
    #return var,mod,scen,mem,tstamp
    return scen,realm,tres,var,mod,mem,tstamp

########################
