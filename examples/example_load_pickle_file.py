'''Script to generate a multi-model ensemble as a list of model objects from
a set of .nc files.

For simulations given as time slices, files are appended so are assumed to be
given in chronological order from the ncdfinfo5 function.

(working from Ouranos workstation)
'''


import matplotlib.pyplot as plt
import sys
from IPython import embed
from netCDF4 import Dataset
import numpy as np
import os
import cPickle as pickle
from itertools import product

import Model as Ens
import cdf2ens as c2e
import netcdfutils

reload(Ens)


inputdir='/home/partanen/data/'


file_pickle=inputdir+'CMIP5-regional-pr-1pctCO2-N2-1seas.pkl'

output = open(file_pickle, 'rb')
mme=pickle.load(output)
output.close()

mme.Show()
mme.Show2()
