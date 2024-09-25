    
import argparse
import glob
import os
import json

def add_args(parser):
    """
    Args:
        parser (argparse.ArgumentParser): the command-line parser
    """

    parser.add_argument("-i", "--input", action="store",
        type=str, default="", dest="input",
        help="comma separated list of json files to join")

    parser.add_argument('-o', "--output", action="store",
        type=str, dest="outfile",
        help="output json file")

# Get params from parser
parser = argparse.ArgumentParser(description="Weight LLP folder")
add_args(parser)
params = vars(parser.parse_args())  # dict()

inputfiles = params["input"].split(",")
print(inputfiles)

new_dict = {}

for filename in inputfiles:
    with open(filename, "r") as f:
        old_dict = json.load(f)
        new_dict.update(old_dict)

with open(params["outfile"], "w") as f:
    json.dump(new_dict, f)


