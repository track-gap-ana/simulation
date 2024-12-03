""" One simulation set incorrectly has all runID = 0. This script will fix that. """

import icecube
from icecube import icetray, dataio, dataclasses
from icecube.icetray import I3Tray
import glob

# # top folder path
# topfolder="/data/user/axelpo/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-150000.0_ene_2000.0_15000.0_gap_100.0_240602.210981234/"

# # get all folder
# filelist = glob.glob(topfolder + "LLP*/*.i3.gz")


filelist = [
'TESTLLPSimulation.210981234.34/LLPSimulation.DarkLeptonicScalar.mass-110.0.eps-3e-05.bias-1000000.0.nevents-500.i3.gz']


def testfunc(frame):
    frame["hi"] = dataclasses.I3Double(-99)
    return True
tray = I3Tray()
tray.Add("I3Reader", "reader", FilenameList=filelist)
# tray.AddModule(testfunc, Streams = [icecube.icetray.I3Frame.DAQ])
# tray.Add("I3Writer", "writer", filename = filelist[0])
tray.Add("I3Writer", "writer", filename = "test.i3")

tray.Execute()
# # get procID from each file
# def id_from_path(filename):
#     # split to get folder with procid
#     folder = filename.split("/")[-2]
#     procid = folder.split('.')[-1]
#     return int(procid)

# # open all files and change I3EventHeader
# # from condor submit: --runid $$([<datasetid>*100000+$(ProcId)]) \
# datasetid = 776*100000

# for filename in filelist:
#     procid = id_from_path(filename)
#     runid = datasetid + procid
#     # open and change all frames
#     with dataio.I3File(filename, 'w') as file:
#         while file.more():
#             print("hello")
#             frame = file.pop_frame()
#             if "I3EventHeader" in frame:
#                 old_header = frame["I3EventHeader"]
#                 new_header = old_header
#                 new_header.run_id = runid
#                 del frame["I3EventHeader"]
#                 print(new_header)
#                 frame["I3EventHeader"] = new_header
#                 file.push(frame)

    