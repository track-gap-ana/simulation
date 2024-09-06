import pandas as pd
import pylab as plt
import simweights
import numpy as np
import math


corsika_filepath = "/data/user/axelpo/LLP-at-IceCube/dark-leptonic-scalar-simulation/spectrum-at-detector-boundary/Trigger/Muons_in_ice_30files.hdf5"
n_files = 30

muongun_hoerandel_filepath = "/data/user/axelpo/muongun_weighting_scratch/Hoerandel5_atmod12_SIBYLL/triggered.i3"


muongun_NO_LLP_filepath = "/data/user/axelpo/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-50000.0_ene_50.0_10000.0_gap_50.0_240906.215525070/LLPSimulation.215525070.0/LLPSimulation.DarkLeptonicScalar.mass-110.0.eps-3e-05.bias--1.0.nevents-5000.i3.gz"
counter_filepath = "/data/user/axelpo/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-50000.0_ene_50.0_10000.0_gap_50.0_240906.215525070/LLPSimulation.215525070.0/llp_counter.json"

plot_filename = "comparison_hoerandel_trigger_2024_no_llp.png"

############### LOAD CORSIKA ###############
# load the hdf5 file that we just created using pandas
hdffile = pd.HDFStore(corsika_filepath, "r")
#hdffile = pd.HDFStore("test.hdf5", "r")

# instantiate the weighter object by passing the pandas file to it
weighter = simweights.CorsikaWeighter(hdffile, nfiles = n_files)

# create an object to represent our cosmic-ray primary flux model
flux = simweights.Hoerandel5()

# get the weights by passing the flux to the weighter
weights = weighter.get_weights(flux)

# print some info about the weighting object
print(weighter.tostring(flux))
# print to file
with open("weighting_object_"+str(n_files)+".txt", 'w') as outfile:
    outfile.write(weighter.tostring(flux))


# get energy of the primary cosmic-ray from `PolyplopiaPrimary`
primary_energy = weighter.get_column("PolyplopiaPrimary", "energy")
primary_zenith = weighter.get_column("PolyplopiaPrimary", "zenith")

# muon info
N_track = weighter.get_column("MuonAtDetectorBoundary", "N")
max_energy_track = weighter.get_column("MuonAtDetectorBoundary", "HighestMuonEnergyTrack")
sum_energy_track = weighter.get_column("MuonAtDetectorBoundary", "TotalEnergyTrack")

energy_N1_track = [energy for energy, n in zip(max_energy_track, N_track) if n == 1 ]
weights_N1_track = [weight for weight, n in zip(weights, N_track) if n ==1]
zenith_N1 = [zen for zen, n in zip(primary_zenith, N_track) if n == 1 ]
print("Sum of weights for single muons track:", sum(weights_N1_track))

for N, maxE, sumE in zip(N_track, max_energy_track, sum_energy_track):
    if N == 1 and (maxE != sumE or maxE <= 0):
        print("oh no!", N, maxE, sumE)

############### END CORSIKA ###############

############### LOAD MUONGUN ###############

from icecube.dataclasses import I3Double
import icecube
from icecube import icetray, dataio
from icecube import MuonGun
from icecube.icetray import I3Tray

class total_weight(icetray.I3Module):
    def __init__(self,ctx):
        icetray.I3Module.__init__(self,ctx)

        self.AddParameter("energies", "muon energy", None)
        self.AddParameter("weights", "muon weight", None)
        self.AddParameter("zeniths", "muon zen", None)
        self.AddParameter("generated", "generated", None)

    def Configure(self): 
        self.tot = 0.0
        self.nevents = 0
        self.generated = self.GetParameter("generated")
        self.energies = self.GetParameter("energies")
        self.weights = self.GetParameter("weights")
        self.zeniths = self.GetParameter("zeniths")

    def DAQ(self, frame):
        weight_name = "muongun_weights"
        if weight_name in frame and frame[weight_name] > 0 and frame[weight_name] < 1000000:
            self.tot = self.tot + frame[weight_name].value
            self.weights.append(frame[weight_name].value)
            self.energies.append(frame["MMCTrackList"][0].particle.energy)
            self.zeniths.append(frame["MMCTrackList"][0].particle.dir.zenith)
        self.nevents += 1

        #print(self.tot)
    def Finish(self):
        print("total rate raw", self.tot)
        print("total rate", self.tot/(self.generated - self.nevents))
        print("total events:", self.nevents)

muongun_hoerandel_energies = []
muongun_hoerandel_weights = []
muongun_hoerandel_zeniths = []
tot_generated = 100_000

icetray.set_log_level(icetray.I3LogLevel.LOG_INFO)
tray = I3Tray()
tray.Add("I3Reader", filename=muongun_hoerandel_filepath)
tray.Add(total_weight,
         energies = muongun_hoerandel_energies,
         weights = muongun_hoerandel_weights,
         zeniths = muongun_hoerandel_zeniths,
         generated = tot_generated,
        )
tray.Execute()

# rescale
tot_events = len(muongun_hoerandel_weights)
muongun_hoerandel_weights = [x/(tot_generated - tot_events) for x in muongun_hoerandel_weights]

# for 1e15 case
muongun_1e15_energies = []
muongun_1e15_weights = []
muongun_1e15_zeniths = []
tot_generated = 5000

icetray.set_log_level(icetray.I3LogLevel.LOG_INFO)
tray = I3Tray()
tray.Add("I3Reader", filename=muongun_NO_LLP_filepath)
tray.Add(total_weight,
         energies = muongun_1e15_energies,
         weights = muongun_1e15_weights,
         zeniths = muongun_1e15_zeniths,
         generated = tot_generated,
        )
tray.Execute()

# rescale due to generating 1e15 events in LLP simulation script
tot_events = len(muongun_1e15_weights)
muongun_1e15_weights = [x/(tot_generated - tot_events) for x in muongun_1e15_weights]
print("rescaled weight sum no llp", sum(muongun_1e15_weights))

############### END MUONGUN ###############


############### PLOT ###############

logbins = np.geomspace(50, 1e4, 50)
plt.figure()
plt.hist(energy_N1_track,
         weights = weights_N1_track,
         bins = logbins,
         label = "CORSIKA-in-ice 20904 Hoerandel5",
         alpha=0.5)

plt.hist(muongun_hoerandel_energies,
         weights = muongun_hoerandel_weights,
         bins = logbins,
         label = "MuonGun Hoerandel5",
         alpha=0.5)

plt.hist(muongun_1e15_energies,
         weights = muongun_1e15_weights,
         bins = logbins,
         label = "MuonGun Hoerandel5 NO LLP",
         alpha=0.5)
"""
plt.hist(energy_N1,
         weights = weights_N1,
         bins = logbins,
         label = "CORSIKA GaisserH4a n="+str(len(energy_N1)),
         alpha=0.5)
"""
plt.legend(loc="lower center")
plt.xlabel("Energy [GeV]")
plt.ylabel("Freq. [Hz]")
plt.loglog()
plt.title("Trigger single muon (N=1) energy at MMC volume boundary")
plt.savefig(plot_filename)

# zeniths
plt.figure()
plt.hist(zenith_N1,
         weights = weights_N1_track,
         bins = 50,
         label = "CORSIKA-in-ice 20904 Hoerandel5 n="+str(len(energy_N1_track)),
         alpha=0.5)

plt.hist(muongun_hoerandel_zeniths,
         weights = muongun_hoerandel_weights,
         bins = 50,
         label = "MuonGun Hoerandel5 n="+str(len(muongun_hoerandel_energies)),
         alpha=0.5)

plt.hist(muongun_1e15_zeniths,
         weights = muongun_1e15_weights,
         bins = 50,
         label = "MuonGun Hoerandel5 1e15 n="+str(len(muongun_hoerandel_energies)),
         alpha=0.5)

plt.legend(loc="lower center")
plt.xlabel("Zenith [rad]")
plt.ylabel("Freq. [Hz]")
plt.yscale("log")
plt.title("Trigger single muon (N=1) zenith at MMC volume boundary")
plt.savefig("zeniths_"+plot_filename)

