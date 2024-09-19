""" Takes in files which have SRT cleaned pulses.
    Applies track reconstruction and computes CommonVariables.
"""

import icecube
from icecube import icetray, dataio, offline_filterscripts
from icecube.offline_filterscripts import read_superdst_files
from icecube.icetray import I3Tray

from .segments.track_reco import TrackReco
from .segments.common_variables import ComputeAllCV

import argparse
import os
import glob

def add_args(parser):
    """
    Args:
        parser (argparse.ArgumentParser): the command-line parser
    """

    parser.add_argument("-i", "--inputfolder", action="store",
        type=str, default="", dest="infolder",
        help="folder with .i3 files")
    
    parser.add_argument("-n", "--nfiles", action="store",
        type=int, default=-1, dest="nfiles",
        help="How many i3 file(s) to process. -1 does all.")

    parser.add_argument('-o', "--output", action="store",
        type=str, dest="outputname",
        help="output .i3 name")

# Get params from parser
parser = argparse.ArgumentParser(description="Weight LLP folder")
add_args(parser)
params = vars(parser.parse_args())  # dict()

inputfiles = glob.glob(params["infolder"]+"/*.i3*")[:params["nfiles"]]

cleaned_pulses = "SRTInIcePulses"
subeventstream = "InIceSplit"
reco_particle_name = "MPE_"+cleaned_pulses
bookit = False

tray = I3Tray()

# read in the files
tray.Add("I3Reader", "reader",
         FilenameList=inputfiles)

# track reconstruction (needed for CV)
tray.AddSegment(TrackReco, "track_reco", pulses=cleaned_pulses)

# compute CommonVariables
tableio_keys_to_book = tray.AddSegment(ComputeAllCV, "compute_CV",
                 pulses_map_name = cleaned_pulses,
                 reco_particle_name = reco_particle_name,
                 subeventstream = subeventstream,
                 bookit = bookit,
                 )

# write file
tray.Add("I3Writer", "writer", filename = params["outputname"])

# execute
tray.Execute()