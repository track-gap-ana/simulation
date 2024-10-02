import argparse
import icecube
import icecube.icetray
import icecube.dataclasses

from icecube.icetray import I3Tray
from icecube import dataio, icetray, recclasses
import glob

# create plotter
class Counter(icetray.I3Module):
    def __init__(self, ctx):
        icetray.I3Module.__init__(self, ctx)

    def Configure(self):
        self.nevents = 0
        self.passed = 0
        self.hit_lengths = []
        self.passed_hit_lengths = []
        
    def DAQ(self, frame):
        self.nevents += 1

        if (frame.Has("I3SuperDST") and frame.Has("DSTTriggers") and frame.Has("I3EventHeader")):
            self.passed += 1
            self.passed_hit_lengths.append(frame["I3DST22_InIceSplit0"].ndom)
            trigger = frame["I3Triggers"]
            #print(trigger)
        elif frame.Has("I3DST22_InIceSplit0"):
            dst = frame["I3DST22_InIceSplit0"]
            self.hit_lengths.append(frame["I3DST22_InIceSplit0"].ndom)
            trigger = frame["I3Triggers"]
            self.PushFrame(frame)
#            print(trigger)


    def Finish(self):
        print("Events: ", self.nevents)
        print("Passed: ", self.passed)
        hitdict = {}
        for hits in self.hit_lengths:
            if hits in hitdict:
                hitdict[hits] += 1
            else:
                hitdict[hits] = 1
        print("Hit lengths not passed", hitdict) 
        hitdict = {}
        for hits in self.passed_hit_lengths:
            if hits in hitdict:
                hitdict[hits] += 1
            else:
                hitdict[hits] = 1
        print("Hit lengths passed", hitdict) 
        import matplotlib.pyplot as plt
        bins = list(range(0,100))
        plt.figure()
        plt.hist(self.hit_lengths, label="not passed", bins=bins, alpha=0.5)
        plt.hist(self.passed_hit_lengths, label="passed", bins = bins, alpha=0.5)
        plt.xlim([0,100]) 
        plt.title("Passing online")
        plt.xlabel("NDom")
        plt.legend()
        plt.savefig("compare_hits_online.png")


#### TRIGGER ####

filenamelist = glob.glob("/data/user/axelpo/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-500000.0_ene_200.0_15000.0_gap_50.0_240722.213638022/LLP*/LLP*.gz")

print("### TRIGGER ###")
# tray
#tray = I3Tray()
#tray.AddModule("I3Reader", "reader", FilenameList=filenamelist)
#tray.AddModule(Counter)
#tray.Execute(20000)


#### ONLINE ####

filenamelist = glob.glob("/data/user/vparrish/llp_ana/online/output/lateVirgo/011024/mass-110/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-500000.0_ene_200.0_15000.0_gap_50.0_240722.213638022/*.gz")

print("### ONLINE ###")
# tray
tray = I3Tray()
tray.AddModule("I3Reader", "reader", FilenameList=filenamelist)
tray.AddModule(Counter)
tray.Add("I3Writer", "writer", filename="didnt_pass.i3.gz", Streams=[icetray.I3Frame.DAQ])
tray.Execute(20000)
