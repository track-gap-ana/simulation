""" Creates a json that maps the correct summary.json file to the online processed i3 file.
    
    The online processed i3 files don't have the jobID in the title so need to check runid.
    
    The summary files are needed for weighting.
    """
    
import argparse
import glob
import os
import json

import icecube
from icecube import icetray, dataio

def add_args(parser):
    """
    Args:
        parser (argparse.ArgumentParser): the command-line parser
    """

    parser.add_argument("-i", "--inputfolder", action="store",
        type=str, default="", dest="infolder",
        help="folder with .i3 files")
    
    parser.add_argument("-f", "--basefolder", action="store",
        type=str, default="", dest="basefolder",
        help="folder with original LLP simulation files")

    parser.add_argument('-o', "--output", action="store",
        type=str, dest="outfile",
        help="output json file")

# Get params from parser
parser = argparse.ArgumentParser(description="Weight LLP folder")
add_args(parser)
params = vars(parser.parse_args())  # dict()

if params["infolder"][-1] != "/":
    params["infolder"] += "/"
if params["basefolder"][-1] != "/":
    params["basefolder"] += "/"
    
# get all i3 files
inputfiles = glob.glob(params["infolder"] + "*.i3*")

# create dict
i3_json_dict = {}

# go through each i3 file
for filename in inputfiles:
    # get runid
    f = dataio.I3File(filename)

    fr = f.pop_frame(icetray.I3Frame.Stream('Q'))
    while "I3EventHeader" not in fr:
        fr = f.pop_frame(icetray.I3Frame.Stream('Q'))
    header = fr["I3EventHeader"]
    f.close()
    
    # get summary file for a runid
    runid = str(header.run_id)
    jobid = int(runid[-4:])

    json_file = glob.glob(params["basefolder"] + "*." + str(jobid) + "/summary.json")

    print("Filename and json file")
    print(runid)
#    print(filename)
    print(json_file)
    i3_json_dict[filename] = json_file


with open(params["outfile"],"w") as outfile:
    json.dump(i3_json_dict, outfile)
