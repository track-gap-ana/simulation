import tables
import numpy as np
import os
import argparse
import matplotlib.pyplot as plt

# Create the argument parser
parser = argparse.ArgumentParser(description='Plot all common variables.')
parser.add_argument('-sig', dest="signal", type=str, help='Path to the signal HDF5 file')
parser.add_argument('-bkg', dest="background", type=str, help='Path to the bkg HDF5 file.')

# Parse the command-line arguments
args = parser.parse_args()
params = vars(args)

# load file
signalfile = tables.open_file(params['signal'], 'r')
backgroundfile = tables.open_file(params['background'], 'r')

##### PLOT #####
def plot_hist1D(node_sig, node_bkg, colname, title, path):
    plt.figure()
    plt.title(title)
    plt.hist(node_sig.col(colname), bins=100, alpha=0.5, label="sig", density=True)
    plt.hist(node_bkg.col(colname), bins=100, alpha=0.5, label="bkg", density=True)
    plt.xlabel(colname)
    plt.ylabel("count")
    plt.legend()
    plt.savefig(path)
    plt.close()   

uninteresting = ["Run", "Event", "SubEvent", "SubEventStream", "exists"]
for node_sig, node_bkg in zip(signalfile.root, backgroundfile.root):
    assert node_sig._v_name == node_bkg._v_name
    # skip index nodes
    if node_sig._v_name[0] == '_':
        continue
    
    nodename = node_sig._v_name
    colnames = node_sig.colnames
    
    for colname in colnames:
        if colname not in uninteresting:
            path = "plots/sig_vs_bkg" + "/" + nodename + "/"
            if not os.path.exists(path):
                os.makedirs(path)
            plot_hist1D(node_sig, node_bkg, colname, title = '{}'.format(nodename), path = path + "/" + colname + ".png")






##### OLD ACCESS CODE #####

# ##### HitStatisticsValues #####
# print("HitStatisticsValues")
# hits = hdffile.root.HitStatisticsValues
# print(hits.colnames)
# # print(hits.col("min_pulse_time"))

# ##### HitMultiplicityValues #####
# print("HitMultiplicityValues")
# multiplicity = hdffile.root.HitMultiplicityValues
# print(multiplicity.colnames)

# ##### DirectHits #####
# print("DirectHits")
# dh_A = hdffile.root.PoleMuonLlhFitDirectHitsA
# dh_B = hdffile.root.PoleMuonLlhFitDirectHitsB
# dh_C = hdffile.root.PoleMuonLlhFitDirectHitsC
# dh_D = hdffile.root.PoleMuonLlhFitDirectHitsD

# print(dh_A.colnames)
# print(dh_B.colnames)
# print(dh_C.colnames)
# print(dh_D.colnames)

# ##### TrackCharacteristics #####
# print("TrackCharacteristics")
# track = hdffile.root.PoleMuonLlhFitTrackCharacteristics
# print(track.colnames)

# ##### TimeCharacteristics #####
# print("TimeCharacteristics")
# time = hdffile.root.PoleMuonLlhFitTimeCharacteristics
# print(time.colnames)
