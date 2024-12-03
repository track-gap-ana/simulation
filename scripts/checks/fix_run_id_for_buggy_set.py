""" One simulation set incorrectly has all runID = 0. This script will fix that. """

import icecube
from icecube import icetray, dataio, dataclasses
from icecube.icetray import I3Tray

import os
import glob

parentdir = "/data/user/axelpo/LLP-data/"
folder = "DarkLeptonicScalar.mass-110.eps-3e-05.nevents-150000.0_ene_2000.0_15000.0_gap_100.0_240602.210981234/"

inputfilelist = glob.glob(parentdir+folder+"*/*.gz")
folders = [os.path.dirname(f) for f in inputfilelist]
filenames = [f.split("/")[-1] for f in inputfilelist]

def FixRunID(frame, procid):
    datasetid = 776
    if "OldI3EventHeader" in frame:
        oldheader = frame["OldI3EventHeader"]
        newheader = oldheader
        newrunid = datasetid*100000 + procid
        newheader.run_id = newrunid
        frame["I3EventHeader"] = newheader
    return True

for i, (filepath, folder, name) in enumerate(zip(inputfilelist, folders, filenames)):
    procid = int(folder.split(".")[-1])
    print("Doing file ", name)
    # create tray
    tray = I3Tray()
    tray.Add("I3Reader", "reader", Filename=filepath)
    tray.AddModule("Rename", "rename header", Keys = ["I3EventHeader", "OldI3EventHeader"])
    tray.Add(FixRunID, "fix id", procid=procid, Streams=[icetray.I3Frame.DAQ])
    tray.Add("Delete", "delete old header", Keys=["OldI3EventHeader"])
    tray.Add("I3Writer", "writer", filename=folder+"/fixedid_"+name)
    tray.Execute()