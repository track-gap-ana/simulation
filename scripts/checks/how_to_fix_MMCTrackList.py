""" How to fix MMCTrackList objects that contain muons from LLP decays. """

import icecube
import icecube.icetray as icetray
import icecube.dataclasses
import icecube.dataio
import icecube.simclasses

from icecube.icetray import I3Tray, I3Units

tray = I3Tray()

tray.AddModule("I3Reader", "reader", filename="/home/axel/i3/LLP-data/DarkLeptonicScalar.mass-110.eps-1e-5.nevents-50000_ene_1e3_2e5_gap_100_240503.208637138/L2.i3.gz")

# Add empty MMCTrackList objects for events that have none.
def add_empty_tracklist(frame):
    if "MMCTrackList" not in frame:
        frame["MMCTrackList"] = icecube.simclasses.I3MMCTrackList()
    return True

tray.AddModule(add_empty_tracklist, "_add_empty_tracklist",
            Streams=[icecube.icetray.I3Frame.DAQ])

# fix MMCTrackList "bug" that adds MMCTrack for LLP decay muons (PROPOSAL doesn't know if a muon is from LLP or not)
def FixMMCTrackListLLP(frame, keyname="MMCTrackListLLP"):
    if keyname in frame:
        tracklist_LLP         = frame[keyname]
        # highest energy muon is the initial muon from muongun
        initial_muon          = max(tracklist_LLP, key = lambda track : track.Ei, default = None)
        tracklist_good        = icecube.simclasses.I3MMCTrackList([initial_muon])
        frame["MMCTrackList"] = tracklist_good
        return True
    else:
        print("no ", keyname, " in frame!")
        exit()
        return False
    
# copy over the "buggy" mmctracklist to a new key
tray.AddModule("Rename", "rename MMCTrackList", Keys = ["MMCTrackList", "MMCTrackListLLP"])
tray.Add(FixMMCTrackListLLP, streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics])
tray.Add(lambda frame: print(len(frame["MMCTrackListLLP"])), streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics])
tray.Add(lambda frame: print(len(frame["MMCTrackList"])), streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics])
#tray.Add('Dump')
tray.Execute(10)
