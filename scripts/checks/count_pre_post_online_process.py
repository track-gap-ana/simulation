import argparse
import icecube
import icecube.icetray
import icecube.dataclasses
from icecube.icetray import I3Tray
from icecube import dataio, icetray
import glob

# create plotter
class Counter(icetray.I3Module):
    def __init__(self, ctx):
        icetray.I3Module.__init__(self, ctx)

    def Configure(self):
        self.nevents = 0
        self.passed = 0
        
    def DAQ(self, frame):
        self.nevents += 1
        # Require I3SuperDST, I3EventHeader, and DSTTriggers; delete the rest
        if (frame.Has("I3SuperDST") and frame.Has("DSTTriggers") and frame.Has("I3EventHeader")):
            self.passed += 1
        
        return True

    def Finish(self):
        print("Events: ", self.nevents)
        print("Passed: ", self.passed)

#### TRIGGER ####

filenamelist = glob.glob("/data/user/axelpo/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-500000.0_ene_200.0_15000.0_gap_50.0_240722.213638022/LLP*/LLP*.gz")

print("### TRIGGER ###")
# tray
tray = I3Tray()
tray.AddModule("I3Reader", "reader", FilenameList=filenamelist)
tray.AddModule(Counter)
tray.Execute()

#### ONLINE ####

filenamelist = glob.glob("/data/user/vparrish/llp_ana/online/output/lateVirgo/011024/mass-110/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-500000.0_ene_200.0_15000.0_gap_50.0_240722.213638022/*.gz")

print("### ONLINE ###")
# tray
tray = I3Tray()
tray.AddModule("I3Reader", "reader", FilenameList=filenamelist)
tray.AddModule(Counter)
tray.Execute()

