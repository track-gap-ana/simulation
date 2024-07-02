import icecube
from icecube import icetray, dataio, dataclasses, MuonGun
from icecube.icetray import I3Tray

import os
import numpy as np
import matplotlib.pyplot as plt
import corner

# get the file name with an argparse
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type=str, help="path to the input file")
parser.add_argument("-n", "--nevents", type=int, default=-1, help="number of events to process")
args = parser.parse_args()

filename = args.input
nevents = args.nevents

folder = os.path.dirname(filename)
folder = os.path.join(folder + "/spectrum_plots")
os.makedirs(folder, exist_ok=True)

# funcs
def MakeSurface(gcdName, padding):
    file = dataio.I3File(gcdName, "r")
    frame = file.pop_frame()
    while not "I3Geometry" in frame:
        frame = file.pop_frame()
    geometry = frame["I3Geometry"]
    xyList = []
    zmax = -1e100
    zmin = 1e100
    step = int(len(geometry.omgeo.keys())/10)
    print("Loading the DOM locations from the GCD file")
    for i, key in enumerate(geometry.omgeo.keys()):
        if i % step == 0:
            print( "{0}/{1} = {2}%".format(i,len(geometry.omgeo.keys()), int(round(i/len(geometry.omgeo.keys())*100))))
            
        if key.om in [61, 62, 63, 64] and key.string <= 81: #Remove IT...
            continue

        pos = geometry.omgeo[key].position

        if pos.z > 1500:
            continue

        xyList.append(pos)
        i+=1
    
    return MuonGun.ExtrudedPolygon(xyList, padding)

# create plotter
class Plotter(icetray.I3Module):
    def __init__(self, ctx):
        icetray.I3Module.__init__(self, ctx)
        self.folder = ""
        self.AddParameter("folder", "folder", self.folder)

    def Configure(self):
        self.folder = self.GetParameter("folder")
        assert self.folder != ""
        # lists for histograms
        self.histograms = {"muon_energy": [],
                      "muon_zenith": [],
                      "muon_length": [],
                      "LLP_gap": [],
                      "LLP_energy": [],
                      "LLP_zenith": [],
                      }
        self.surface = MakeSurface("/data/user/axelpo/LLP-at-IceCube/dark-leptonic-scalar-simulation/resources/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz", 0.)
        
    def DAQ(self, frame):
        muon_energy, muon_zenith, muon_length = self.obtain_MC_info(frame, self.surface)
        self.histograms["muon_energy"].append(muon_energy)
        self.histograms["muon_zenith"].append(muon_zenith)
        self.histograms["muon_length"].append(muon_length)
        # LLP info
        llpinfo = frame["LLPInfo"]
        self.histograms["LLP_gap"].append(llpinfo["length"])
        self.histograms["LLP_energy"].append(llpinfo["llp_energy"])
        self.histograms["LLP_zenith"].append(llpinfo["zenith"])
        return True
    
    def obtain_MC_info(self, frame, surface=None):
        """ Return MC muon info. Energy, zenith and length in detector.
            If many muons, then compute sum of energies.
        """
        if "MMCTrackList" not in frame:
            raise ValueError("MMCTrackList not in frame")
        tracklist = frame["MMCTrackList"]
        muon_energy = 0
        # iterate through MMCTrackList
        for track in tracklist:
            muon_energy += track.Ei

        # get muon zenith
        muon_zenith = tracklist[0].particle.dir.zenith

        # get muon length
        intersections = surface.intersection(tracklist[0].particle.pos, tracklist[0].particle.dir)
        muon_length = intersections.second - intersections.first

        assert intersections.second > intersections.first

        return muon_energy, muon_zenith, muon_length

    def Finish(self):
        # write to file
        import pandas as pd
        df = pd.DataFrame(self.histograms)
        df.to_csv(self.folder + "/spectrum.csv")
        # plot
        for key in self.histograms.keys():
            plt.figure()
            plt.hist(self.histograms[key], bins=100, histtype="step", label=key)
            plt.legend()
            path = os.path.join(self.folder, f"{key}.png")
            plt.savefig(path)
            plt.close()
        # corner plots
        # Create a list of performance variable values
        keys = list(self.histograms.keys())
        try:
            keys.remove("LLP_zenith")
        except:
            pass
        vals = [self.histograms[key] for key in keys]
        
        # Plot the histogram triangle
        print("Creating corner plot")
        figure = corner.corner(
            np.transpose(vals),
            labels=keys,
            show_titles=True,
            title_fmt=".2f",
            bins=100,
            plot_contours=True,
            smooth=True,
            # axes_scale="log",
        )
        plt.savefig(self.folder + "/corner.png")

# tray
tray = I3Tray()
# reader
tray.AddModule("I3Reader", "reader", Filename=filename)
tray.AddModule(Plotter, folder=folder)

if nevents == -1:
    tray.Execute()
else:
    tray.Execute(nevents)