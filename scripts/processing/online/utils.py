import matplotlib.pyplot as plt
import icecube
import numpy as np
import os
from icecube import icetray, dataio, dataclasses, simclasses

##### PLOT #####
def plot_hist1D(node, colname, title, path, weights = None, density = False):
    plt.figure()
    plt.title(title)
    plt.hist(node.col(colname), bins=100, weights = weights, density = density)
    plt.xlabel(colname)
    if density:
        plt.ylabel("Density")
    else:
        plt.ylabel("Count")
    plt.savefig(path)
    plt.close()
    
def plot_hist1D_compare(node, colname, title, path, weights):
    plt.figure()
    plt.title(title)
    plt.hist(node.col(colname), bins=100, 
             weights = None, 
             density = True, 
             label = "Unweighted", 
             alpha=0.5
            )
    plt.hist(node.col(colname), bins=100,
             weights = weights, 
             density = True, 
             label = "Weighted", 
             alpha=0.5
            )
    plt.xlabel(colname)
    plt.ylabel("Density")
    plt.legend()
    plt.savefig(path)
    plt.close()
    
def plot_hist_comparison(node_1, node_2, colname, title, path, weights_1, weights_2, label_1, label_2):
    plt.figure()
    plt.title(title)
    # @TODO: ad hoc ugly. shuold do a map for names to log/lin scale
    if node_1._v_name == "MuonAtMMCBoundary":
        plt.xscale("log")
        plt.yscale("log")
        bins = np.logspace(np.log10(np.min(node_2.col(colname))), np.log10(np.max(node_2.col(colname))), 100)
    else:
        bins = 100
    plt.hist(node_1.col(colname), bins=bins, 
             weights = weights_1, 
             density = True, 
             label = label_1, 
             alpha=0.5
            )
    plt.hist(node_2.col(colname), bins=bins,
             weights = weights_2, 
             density = True, 
             label = label_2, 
             alpha=0.5
            )
    plt.xlabel(colname)
    plt.ylabel("Density")
    plt.legend()
    plt.savefig(path)
    plt.close()
################

class MMCTrackListExtractor(icetray.I3Module):
    """
        This module is for atmospheric muon information at the MMC boundary
    """
    def __init__(self,ctx):
        icetray.I3Module.__init__(self,ctx)

    def DAQ(self, frame):

        tracklist = frame["MMCTrackList"]
        muon_energies_tracklist = [track.Ei for track in tracklist]
        
        # save to frame
        muon_map                      = dataclasses.I3MapStringDouble()
        muon_map["HighestMuonEnergy"] = max(muon_energies_tracklist)
        muon_map["TotalEnergy"]       = sum(muon_energies_tracklist)
        muon_map["N_track"]           = len(muon_energies_tracklist)
        frame["MuonAtMMCBoundary"]    = muon_map
        self.PushFrame(frame)
        
        
def weight_CORSIKA_hdf5(inputfile: str, nCORSIKA: int):
    """ Weighs a CORSIKA -> hdf5 file.
    Returns HDFStore object and event weights.
    """
    import simweights
    import pandas as pd

    # load the hdf5 file that we just created using pandas
    hdffile = pd.HDFStore(inputfile, "r")
    
    # instantiate the weighter object by passing the pandas file to it
    weighter = simweights.CorsikaWeighter(hdffile, nfiles = nCORSIKA)
    
    # create an object to represent our cosmic-ray primary flux model
    flux = simweights.Hoerandel5()
    
    # get the weights by passing the flux to the weighter
    weights = weighter.get_weights(flux)
    
    # print some info about the weighting object
    print(weighter.tostring(flux))

    return hdffile, weights

############### plot hdf5 file ######################
def plot_CV_from_hdf(hdffile, 
                     uninteresting_nodes, 
                     uninteresting_cols, 
                     basename,
                     weights
                     ):
    # make plots
    for node in hdffile.root:
        # skip index nodes and uninteresting nodes
        if node._v_name[0] == '_':
            continue
        skip = False
        for bad_name in uninteresting_nodes:
            if bad_name in node._v_name:
                skip = True
        if skip:
            print("Skipping node", node)
            continue
        
        nodename = node._v_name
        colnames = node.colnames
        
        for colname in colnames:
            if colname not in uninteresting_cols:
                # plot unweighted
                path = "plots/" + basename + "/unweighted/" + nodename + "/"
                if not os.path.exists(path):
                    os.makedirs(path)
                plot_hist1D(node, colname, title = '{} {}'.format(basename, nodename),
                            path = path + colname + ".png")
                # plot weighted
                path = "plots/" + basename + "/weighted/" + nodename + "/"
                if not os.path.exists(path):
                    os.makedirs(path)
                plot_hist1D(node, colname, title = '{} {}'.format(basename, nodename),
                            path = path + colname + ".png",
                            weights = weights, density = True)
                # plot weighted vs. unweighted
                path = "plots/" + basename + "/weighted_vs_unweighted/" + nodename + "/"
                if not os.path.exists(path):
                    os.makedirs(path)
                plot_hist1D_compare(node, colname, title = '{} {}'.format(basename, nodename),
                            path = path + colname + ".png",
                            weights = weights)


########################3
def plot_CV_comparison(hdffile_1, hdffile_2,
                       weights_1, weights_2, 
                       name_1, name_2,
                       uninteresting_nodes,
                       uninteresting_cols,
                       ):
    # names for plot titles, etc.
    basename = "compare_" + name_1 + "_vs_" + name_2
    label_1 = "LLP"
    label_2 = "CORSIKA"
    
    # get all the nodes that match from the two files, probably a cleaner way exists
    node_dict = {}
    node_1_list = []
    # get interesting nodenames from first file
    for node_1 in hdffile_1.root:
        # skip index nodes and uninteresting nodes
        if node_1._v_name[0] == '_':
            continue
        skip = False
        for bad_name in uninteresting_nodes:
            if bad_name in node_1._v_name:
                skip = True
        if skip:
            print("Skipping node", node_1)
            continue
        # add interestnig node to dict
        node_dict[node_1._v_name] = [node_1]
    
    # add interesting nodes from second file
    for node_2 in hdffile_2.root:
        if node_2._v_name in node_dict:
            node_dict[node_2._v_name].append(node_2)

    # make plots
    for name, node_list in node_dict.items():
        # check if both files have the node
        if len(node_list) != 2:
            continue
        print(name)
        node_1 = node_list[0]
        node_2 = node_list[1]
        
        nodename = node_1._v_name
        colnames = node_1.colnames
        
        for colname in colnames:
            if colname not in uninteresting_cols:
                # plot unweighted
                path = "plots/" + basename + "/unweighted/" + nodename + "/"
                if not os.path.exists(path):
                    os.makedirs(path)
                plot_hist_comparison(node_1, node_2, colname, nodename, path + colname + ".png", None, None, label_1, label_2)
                # plot weighted
                path = "plots/" + basename + "/weighted/" + nodename + "/"
                if not os.path.exists(path):
                    os.makedirs(path)
                plot_hist_comparison(node_1, node_2, colname, nodename, path + colname + ".png", weights_1, weights_2, label_1, label_2)
