""" Converts LLP MC with CommonVariables to hdf5. """

import icecube
from icecube import icetray, dataio, dataclasses, simclasses
from icecube.icetray import I3Tray
from icecube import hdfwriter

from segments.track_reco import TrackReco
from segments.common_variables import ComputeAllCV

import argparse
import glob

# MMCTrackListExtractor
from utils import *

def add_args(parser):
    """
    Args:
        parser (argparse.ArgumentParser): the command-line parser
    """

    parser.add_argument("-i", "--inputfolder", action="store",
        type=str, default="", dest="infolder",
        help="folder with .i3 files")

    parser.add_argument('-o', "--outputfile", action="store",
        type=str, dest="outfile",
        help="output .hdf5 name")

# Get params from parser
parser = argparse.ArgumentParser(description="Weight LLP folder")
add_args(parser)
params = vars(parser.parse_args())  # dict()

if params["infolder"][-1] != "/":
    params["infolder"] += "/"

inputfiles = glob.glob(params["infolder"] + "*.i3*")

# settings used for CV
cleaned_pulses = "SRTInIcePulses"
subeventstream = "InIceSplit"
reco_particle_name = "MPE_"+cleaned_pulses

##### KEYS TO SAVE TO HDF5 #####
# header, weight, llpinfo, etc.
event_keys = [
    "I3EventHeader",
    "muongun_weights",
    "LLPInfo"
    ]
# common variables
CV_keys = [
    'HitMultiplicityValues',
    'HitStatisticsValues',
    reco_particle_name+'TimeCharacteristics',
    reco_particle_name+'TrackCharacteristics',
    reco_particle_name+'DirectHits'+'A',
    reco_particle_name+'DirectHits'+'B',
    reco_particle_name+'DirectHits'+'C',
    reco_particle_name+'DirectHits'+'D',
    ]
# muon spectrum info
muon_keys = [
    "MuonAtMMCBoundary",
    #"I3MCTree_preMuonProp",
    ]

keys_to_save = event_keys + CV_keys + muon_keys
################################


tray = I3Tray()

# read in the files
tray.Add("I3Reader", "reader", FilenameList = inputfiles)

# get info from MMCTrackList in a deserializable form (whatever that means)
tray.Add(MMCTrackListExtractor)

print("Writing %s to HDF5 file: %s" % (keys_to_save, params["outfile"]))
tray.AddSegment(hdfwriter.I3HDFWriter, 'hdfwriter',
    Keys            = keys_to_save,
    SubEventStreams = [subeventstream],
    Output          = params["outfile"]
)

# execute
tray.Execute()
