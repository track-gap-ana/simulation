""" Take in a folder of LLP files and weight them. """

import os
import glob
import argparse
import matplotlib.pyplot as plt
import numpy as np

import icecube
from icecube import dataio, icetray, MuonGun
from icecube.icetray import I3Tray

import llp_simulation.weighting.weighting as weighting

class Plotter(icetray.I3Module):
    def __init__(self, ctx):
        icetray.I3Module.__init__(self, ctx)
        # add parameter
        self.AddParameter("weightname", "weight name", "MuonWeight")

    def Configure(self):
        # get parameters
        self.weightname = self.GetParameter("weightname")
        # lists for plotting
        self.original_weights = []
        self.weights = []
        self.energies = []
        # counter
        self.nevents = 0
        self.bad_weights = 0

    def DAQ(self, frame):
        # reweighted values
        if self.weightname in frame:
            w = frame[self.weightname].value
            # check for nan and inf
            if w == w and w < 1000000000000000000000:
                self.weights.append(w)
                self.energies.append(frame["MMCTrackList"][0].particle.energy)
                if "muongun_weights" in frame:
                    self.original_weights.append(frame["muongun_weights"].value)
                # counter
                self.nevents += 1
            else:
                self.bad_weights += 1
        
    def Finish(self):
        print("Total events:", self.nevents)
        print("Bad weights:", self.bad_weights)
        print("Sum of weights:", sum(self.weights))
        print("Sum of original weights:", sum(self.original_weights))

        # Convert lists to numpy arrays
        energies = np.array(self.energies)
        weights = np.array(self.weights)
        if len(self.original_weights) > 0:
            original_weights = np.array(self.original_weights)
        else:
            original_weights = np.ones(len(energies))
        
        # create log bins
        nbins=75
        bins = np.logspace(np.log10(min(self.energies)), np.log10(max(self.energies)), nbins)
        
        # Plot histogram
        density=True
        plt.figure()
        plt.title("Density")
        plt.hist(energies, bins=bins, weights=original_weights, density=density, label = "original", alpha=0.5)
        plt.hist(energies, bins=bins, weights=weights, density=density, label = "recalculated", alpha=0.5)
        plt.hist(energies, bins=bins, density=density, label = "unweighted", alpha=0.5)
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel('Energy')
        plt.ylabel('Density')
        plt.legend()
        
        plt.figure()
        plt.title("Only unweighted")
        plt.hist(energies, bins=bins, label = "unweighted")
        plt.xscale("log")
        
        # Plot histogram
        density=True
        plt.figure()
        plt.title("Density linear")
        plt.hist(energies, bins=bins, weights=original_weights, density=density, label = "original", alpha=0.5)
        plt.hist(energies, bins=bins, weights=weights, density=density, label = "recalculated", alpha=0.5)
        plt.hist(energies, bins=bins, density=density, label = "unweighted", alpha=0.5)
        plt.xscale("log")
        # plt.yscale("log")
        plt.xlabel('Energy')
        plt.ylabel('Density')
        plt.legend()
        
        density = False
        plt.figure()
        plt.title("Rate")
        # plt.hist(energies, bins=bins, weights=original_weights, density=density, label = "original", alpha=0.5)
        plt.hist(energies, bins=bins, weights=weights, density=density, label = "Tot rate: {:.2f} Hz".format(sum(self.weights)), alpha=0.5)
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel('Energy')
        plt.ylabel('Rate [Hz]')
        plt.legend()
        
        plt.show()
        # plt.close()
###############################################

def add_args(parser):
    """
    Args:
        parser (argparse.ArgumentParser): the command-line parser
    """

    parser.add_argument("--model", dest="model",
                        default="Hoerandel5_atmod12_SIBYLL",
                        type=str, required=False,
                        help="primary cosmic-ray flux parametrization")
    
    parser.add_argument("-i", "--inputfolder", action="store",
        type=str, default="", dest="infolder",
        help="Input i3 file(s)  (use comma separated list for multiple files)")
    
    parser.add_argument("-n", "--nfiles", action="store",
        type=int, default=-1, dest="nfiles",
        help="How many i3 file(s) to process. -1 does all.")

# Get params from parser
parser = argparse.ArgumentParser(description="Weight LLP folder")
add_args(parser)
params = vars(parser.parse_args())  # dict()

nfiles=params["nfiles"]

# get infiles and summaryfiles, make sure they are in the same order
infiles = glob.glob(params["infolder"] + "*/LLP*.i3.gz")[:nfiles]
countfiles = glob.glob(params["infolder"] + "*/llp_counter.json")[:nfiles]
# check order
for file, count in zip(infiles, countfiles):
    if file.split("/")[:-1] != count.split("/")[:-1]:
        print("Files are not in the same order")
        exit()

############### start weighting ###################
model = MuonGun.load_model(params["model"])

# get total muons generated from summary files
tot_mu_generated_list = weighting.get_tot_mu_generated_list(countfiles, key="total")
# get muongun generator
generator = weighting.harvest_rescaled_generators(infiles, tot_mu_generated_list)
print("Generator:", generator)
print("Total event:", generator.total_events)

# tray
icetray.set_log_level(icetray.I3LogLevel.LOG_INFO)

tray = I3Tray()

tray.Add("I3Reader", filenamelist=infiles)
tray.AddModule('I3MuonGun::WeightCalculatorModule', 'MuonWeight', Model=model, Generator=generator)
tray.AddModule(Plotter)

tray.Execute()