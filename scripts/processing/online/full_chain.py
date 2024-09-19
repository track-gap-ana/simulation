import icecube
from icecube import icetray, dataio, offline_filterscripts
from icecube.offline_filterscripts import read_superdst_files
from icecube.icetray import I3Tray

from segments.srt_clean import SRTClean
from segments.track_reco import TrackReco
from segments.common_variables import ComputeAllCV

import argparse
import glob
import os

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
    
    parser.add_argument('-g', '--gcdfile', action="store",
        type=str, dest="gcdfile",
        help="gcdfile")

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

# settings
cleaned_pulses = "SRTInIcePulses"
uncleaned_pulses = "SplitInIcePulses"
subeventstream = "InIceSplit"
reco_particle_name = "MPE_"+cleaned_pulses
bookit = True

# for each file
for inputfile in inputfile_list:
    # create output filename
    basename_out = "CV_" + os.path.basename(inputfile)
    outname = params["outfolder"] + basename_out
    
    print("Processing %s to %s" % (inputfile, outname))
    
    # create tray
    tray = I3Tray()
    # open files
    tray.AddSegment(read_superdst_files.read_superdst_files, 'read_superdst_files',
                    input_files = [inputfile],
                    input_gcd = params["gcdfile"],
    )
    # SRT clean pulses
    tray.AddSegment(SRTClean, "srt_cleaning", input_pulses=uncleaned_pulses, output_pulses=cleaned_pulses)
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
    tray.Add("I3Writer", "writer", filename=outname)
    # execute
    tray.Execute()
