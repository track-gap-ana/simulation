""" Check for corrupt files etc. in the simulation set. """

import argparse
import glob
import shutil
import os
from icecube import icetray, dataio

# sim top folder
parser = argparse.ArgumentParser(description='Check for corrupt files in the simulation set.')
parser.add_argument('-f', '--folder', type=str, help='Path to the folder containing the simulations')
parser.add_argument('--remove-bad', dest="remove_bad", action='store_true', default=False, help='Remove bad files?')
parser.add_argument('-g', '--glob-string', type=str, dest="glob_string", default = '*/*.i3.gz', help='What to search for in the folder.')

args = parser.parse_args()

# check for backslash
if args.folder[-1] != '/':
    args.folder += '/'
print("Checking folder:", args.folder)

# files
filelist = glob.glob(args.folder + args.glob_string)
print("Folder contains %i files."%len(filelist))

# check read access
for f in filelist:
    if not os.access(f,os.R_OK):
        raise Exception('Cannot read from %s'%f)

# check each file
badfiles = []
print("Start checking files:")
for i, file in enumerate(filelist):
    frame_counter = {}
    with dataio.I3File(file) as f:
        while f.more():
            try:
                frame = f.pop_frame()
            except:
                print("Error popping frame in file ", file)
                print("Current frame_counter:", frame_counter)
                print("Moving to next file!")
                badfiles.append(file)
                break # move to next file
            stop = frame.Stop.id
            if stop in frame_counter:
                frame_counter[stop] += 1
            else:    
                frame_counter[stop] = 1
        print("Checked file ", i, " with frames:", frame_counter)

# write bad files to a textfile
print("Bad files:", badfiles)
if args.glob_string != '*/*.i3.gz':
    print("NOT DEFAULT GLOB STRING! DONT DELETE STUFF CUS YOU MIGHT DELTE WHIOLE FOLDER")
    exit()
if args.remove_bad:
    if badfiles == []:
        print("No bad files found.")
        exit()
    parentfolder = os.path.dirname(os.path.dirname(badfiles[0]))
    print("Writing bad file list to ", parentfolder)
    with open(parentfolder + "/bad_files_removed.txt", "w") as f:
        for b in badfiles:
            f.write(b + "\n")
    # delete
    for f in badfiles:
        dir_path = os.path.dirname(f)
        # Check if the directory exists before trying to delete it
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"The directory {dir_path} has been deleted successfully.")
        else:
            print(f"The directory {dir_path} does not exist.")

        
