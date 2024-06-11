""" Check for corrupt files etc. in the simulation set. """

import argparse
import glob
import os
from icecube import icetray, dataio

# sim top folder
parser = argparse.ArgumentParser(description='Check for corrupt files in the simulation set.')
parser.add_argument('-f', '--folder', type=str, help='Path to the folder containing the simulations')

args = parser.parse_args()

# check for backslash
if args.folder[-1] != '/':
    args.folder += '/'
print("Checking folder:", args.folder)

# files
filelist = glob.glob(args.folder + '*/*.i3.gz')
print("Folder contains %i files."%len(filelist))

# check read access
for f in filelist:
    if not os.access(f,os.R_OK):
        raise Exception('Cannot read from %s'%f)

# check each file
badfiles = []
for file in filelist:
    print("Checking file:", file)
    frame_counter = {}
    with dataio.I3File(file) as f:
        while f.more():
            try:
                frame = f.pop()
            except:
                print("Error popping frame!")
                print("Current frame_counter:", frame_counter)
                print("Moving to next file!")
                badfiles.append(file)
                break # move to next file
            stop = frame.Stop
            if stop in frame_counter:
                frame_counter[stop] += 1
            else:    
                frame_counter[stop] = 1
    print(frame_counter)