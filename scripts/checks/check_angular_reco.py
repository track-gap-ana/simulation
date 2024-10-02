import argparse
import icecube
import icecube.icetray
import icecube.dataclasses
import numpy as np


from icecube.icetray import I3Tray
from icecube import dataio, icetray, recclasses
import glob
from icecube.phys_services.which_split import which_split

def angular_difference(phi1, eta1, phi2, eta2):
    dphi = np.abs(phi1 - phi2)
    # if dphi > np.pi:
    #     dphi = 2*np.pi - dphi
    deta = np.abs(eta1 - eta2)
    return np.sqrt(dphi**2 + deta**2)

# create plotter
class Plotter(icetray.I3Module):
    def __init__(self, ctx):
        icetray.I3Module.__init__(self, ctx)

    def Configure(self):
        self.true_zen = []
        self.true_azi = []
        self.keys = ["MPE_SRTInIcePulses",
                "SPE1st_SRTInIcePulses",
                "linefit_SRTInIcePulses",
        ]
        self.reco_zen = {}
        self.reco_azi = {}
        for key in self.keys:
            self.reco_zen[key] = []
            self.reco_azi[key] = []
        
    def Physics(self, frame):
        if frame["I3EventHeader"].sub_event_stream != "InIceSplit":
            return
        llp_info = frame["LLPInfo"]
        self.true_zen.append(llp_info["zenith"])
        self.true_azi.append(llp_info["azimuth"])
        # recos

        for key in self.keys:
            if key in frame:
                reco = frame[key]
                self.reco_zen[key].append(reco.dir.zenith)
                self.reco_azi[key].append(reco.dir.azimuth)


    def Finish(self):
        # convert to np arrays
        self.true_zen = np.array(self.true_zen)
        self.true_azi = np.array(self.true_azi)
        for key in self.keys:
            self.reco_zen[key] = np.array(self.reco_zen[key])
            self.reco_azi[key] = np.array(self.reco_azi[key])
        # histogram reco differences
        import matplotlib.pyplot as plt
        bins = np.linspace(0, 180, 100)
        plt.figure()
        plt.title("Zenith")
        plt.hist(self.true_zen*180/(np.pi), label="True", bins=bins, alpha=0.5)
        for key in self.keys:
            plt.hist(self.reco_zen[key]*180/(np.pi), label=key.split("_")[0],bins = bins, alpha=0.5)
        plt.xlabel("Degrees")
        plt.legend()
        plt.savefig("reco_zenith.png")
        
        bins = np.linspace(-180, 180, 100)
        plt.figure()
        plt.title("Zenith error")
        for key in self.keys:
            plt.hist((self.reco_zen[key] - self.true_zen)*180/(np.pi), label=key.split("_")[0],bins = bins, alpha=0.5)
        plt.xlabel("Degrees")
        plt.yscale("log")
        plt.legend()
        plt.savefig("reco_error_zenith.png")
        
        # total angle error
        bins = np.logspace(-4, np.log10(180), 100)
        plt.figure()
        plt.title("Angular error")
        for key in self.keys:
            abs_error = angular_difference(self.reco_azi[key], self.reco_zen[key], self.true_azi, self.true_zen)
            plt.hist(abs_error*180/(np.pi), label=key.split("_")[0],bins = bins, alpha=0.5)
        plt.xlabel("Degrees")
        plt.yscale("log")
        plt.xscale("log")
        plt.legend()
        plt.savefig("reco_error_all.png")

#### TRIGGER ####

filenamelist = glob.glob("/home/axel/i3/processed-MC/CV_DarkLeptonicScalar.mass-110.eps-3e-05.nevents-500000.0_ene_200.0_15000.0_gap_50.0_240722.213638022/*.gz")

# tray
splitname = "InIceSplit"
tray = I3Tray()
tray.AddModule("I3Reader", "reader", FilenameList=filenamelist)
tray.Add(Plotter)
tray.Execute()

