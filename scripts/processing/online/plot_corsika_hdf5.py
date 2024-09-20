import tables
import numpy as np
import os
import argparse
import matplotlib.pyplot as plt

from utils import *

# Create the argument parser
parser = argparse.ArgumentParser(description='Plot all common variables.')
parser.add_argument('-i', dest="input", type=str, help='Path to the HDF5 file')
parser.add_argument('-n', dest="nfiles", type=int, help="nfiles of corsika.")

# Parse the command-line arguments
args = parser.parse_args()
params = vars(args)

# load file
filename = params['input']
basename = os.path.basename(filename)

hdffile, weights = weight_CORSIKA_hdf5(filename, params["nfiles"])
hdffile.close() # close the pandas opened hdffile
# open hdffile with tables
hdffile = tables.open_file(filename, 'r')

print("hdffile")
print(hdffile)

# don't plot this
uninteresting_cols = ["Run", "Event", "SubEvent", "SubEventStream", "exists"]
uninteresting_nodes = ["I3MCTree_preMuonProp", "I3EventHeader"]

# columns that should be plotted on log scale. energy for example
log_cols = ["TotalEnergy", "HighestMuonEnergy", "N_track"]

plot_CV_from_hdf(hdffile, 
                uninteresting_nodes, 
                uninteresting_cols, 
                basename,
                weights
)

# close file
hdffile.close()