""" 
    This scripts compares the CommonVariables for a set of CORSIKA and LLP simulation.
    Input is two .hdf5 files and nfiles used for CORSIKA.
"""

from utils import *
import tables
import argparse

# Create the argument parser
parser = argparse.ArgumentParser(description='Plot all common variables.')
parser.add_argument('-llp', dest="inputllp", type=str, help='Path to the HDF5 file')
parser.add_argument('-cor', dest="inputcor", type=str, help='Path to the HDF5 file')
parser.add_argument('-n', dest="nfiles", type=int, help="nfiles of corsika.")

# Parse the command-line arguments
args = parser.parse_args()
params = vars(args)

print("Using files (LLP and CORSIKA):", params["inputllp"], params["inputcor"])
print("Nfiles for CORSIKA:", params["nfiles"])
##### GET LLP #####
print("Opening LLP file")
hdffile_1 = tables.open_file(params["inputllp"], 'r')
print("Getting LLP weights")
weights_1 = hdffile_1.root.muongun_weights.col("value")
name_1 = os.path.basename(params["inputllp"])

##### GET CORSIKA #####
print("Opening CORSIKA file and getting weights")
hdffile_pd, weights_2 = weight_CORSIKA_hdf5(params["inputcor"], params["nfiles"])
hdffile_pd.close() # close the pandas opened hdffile and open with tables
hdffile_2 = tables.open_file(params["inputcor"], 'r')
name_2 = os.path.basename(params["inputcor"])

##### PLOT #####
# don't plot this
uninteresting_cols = ["Run", "Event", "SubEvent", "SubEventStream", "exists"]
uninteresting_nodes = ["I3MCTree_preMuonProp"]

# plot
print("Start plotting")
plot_CV_comparison(hdffile_1, hdffile_2,
                       weights_1, weights_2, 
                       name_1, name_2,
                       uninteresting_nodes,
                       uninteresting_cols,
                       )

# close files
hdffile_1.close()
hdffile_2.close()