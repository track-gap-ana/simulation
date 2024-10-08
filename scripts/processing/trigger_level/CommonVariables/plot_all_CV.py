import tables
import numpy as np
import os
import argparse
import matplotlib.pyplot as plt

# Create the argument parser
parser = argparse.ArgumentParser(description='Plot all common variables.')
parser.add_argument('-i', dest="input", type=str, help='Path to the HDF5 file')

# Parse the command-line arguments
args = parser.parse_args()
params = vars(args)

# load file
filename = params['input']
hdffile = tables.open_file(filename, 'r')

print("hdffile")
print(hdffile)

##### PLOT #####
def plot_hist1D(node, colname, title, path):
    plt.figure()
    plt.title(title)
    plt.hist(node.col(colname), bins=100)
    plt.xlabel(colname)
    plt.ylabel("count")
    plt.savefig(path)
    plt.close()   

uninteresting = ["Run", "Event", "SubEvent", "SubEventStream", "exists"]
for node in hdffile.root:
    # skip index nodes
    if node._v_name[0] == '_':
        continue
    
    nodename = node._v_name
    colnames = node.colnames
    
    for colname in colnames:
        if colname not in uninteresting:
            path = "plots/" + filename + "/" + nodename + "/"
            if not os.path.exists(path):
                os.makedirs(path)
            plot_hist1D(node, colname, title = '{} {}'.format(filename, nodename), path = path + "/" + colname + ".png")






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
