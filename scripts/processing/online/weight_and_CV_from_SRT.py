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

    parser.add_argument('-o', "--outputfolder", action="store",
        type=str, dest="outfolder",
        help="output foldername")

# Get params from parser
parser = argparse.ArgumentParser(description="Weight LLP folder")
add_args(parser)
params = vars(parser.parse_args())  # dict()

# create outfolder if doesn't exi
if params["outfolder"][-1] != "/":
    params["outfolder"] += "/"
if params["infolder"][-1] != "/":
    params["infolder"] += "/"

# create model dir if it does not exist
if not os.path.exists(params["outfolder"]):
    os.makedirs(params["outfolder"])
# get list of inputfiles
inputfile_list = glob.glob(params["infolder"] + "*.i3*")[:params["nfiles"]]

cleaned_pulses = "SRTInIcePulses"
subeventstream = "InIceSplit"
reco_particle_name = "MPE_"+cleaned_pulses
bookit = True


# for each file
for inputfile in inputfile_list:
    # create output filename
    basename_out = "CV_" + os.path.basename(inputfile)
    outname = params["outfolder"] + basename_out
    
    print("Processing %s to %s" % (inputfile, outname))
    
    tray = I3Tray()

    # read in the files
    tray.Add("I3Reader", "reader",
            Filename=inputfile)

    # track reconstruction (needed for CV)
    tray.AddSegment(TrackReco, "track_reco", pulses=cleaned_pulses)

    # compute CommonVariables
    tray.AddSegment(ComputeAllCV, "compute_CV",
                    pulses_map_name = cleaned_pulses,
                    reco_particle_name = reco_particle_name,
                    subeventstream = subeventstream,
                    bookit = bookit,
                    )

    # save files
    tray.Add("I3Writer", "writer", filename=outname,
            Streams = [icetray.I3Frame.TrayInfo,
                       icetray.I3Frame.Simulation,
                       icetray.I3Frame.DAQ,
                       icetray.I3Frame.Physics],
            DropOrphanStreams=[icetray.I3Frame.Geometry,
                            icetray.I3Frame.Calibration,
                            icetray.I3Frame.DetectorStatus]
    )
    
    # execute
    tray.Execute()