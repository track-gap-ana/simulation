import tables
import numpy as np
import os
import argparse
import matplotlib.pyplot as plt

from utils import *

# Create the argument parser
parser = argparse.ArgumentParser(description='Plot all common variables.')
parser.add_argument('-i', dest="input", type=str, help='Path to the HDF5 file')

# Parse the command-line arguments
args = parser.parse_args()
params = vars(args)

# load file
filename = params['input']
basename = os.path.basename(filename)
hdffile = tables.open_file(filename, 'r')

print("hdffile")
print(hdffile)

# get weights
weights = hdffile.root.muongun_weights.col("value")

# don't plot this
uninteresting_cols = ["Run", "Event", "SubEvent", "SubEventStream", "exists"]
uninteresting_nodes = ["I3MCTree_preMuonProp"]

plot_CV_from_hdf(hdffile, 
                uninteresting_nodes, 
                uninteresting_cols, 
                basename,
                weights
)

# close file
hdffile.close()