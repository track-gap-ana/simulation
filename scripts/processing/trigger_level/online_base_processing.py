""" This script applies online base processing in the new filtering scheme to simulated DAQ frames. """

import icecube
import icecube.icetray
from icecube import icetray
from icecube import dataio
from icecube.icetray import I3Tray
import icecube.online_filterscripts.base_segments.base_processing as base_processing

import argparse
import glob
import os

# create argparse for input and output files
parser = argparse.ArgumentParser()
parser.add_argument("--inputfile", "-i", help="input DAQ i3 file", default="")
parser.add_argument("--inputfolder", "-f", help="input folder with DAQ i3 files", default="")
parser.add_argument("--gcdfile", "-g", help="GCD file", default="/data/user/axelpo/LLP-at-IceCube/dark-leptonic-scalar-simulation/resources/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz")
parser.add_argument("--outputfile", "-o", help="output i3 file after processing", default="base_processed.i3.gz")

args = parser.parse_args()

# check if folder or file is given
if args.inputfolder != "" and args.inputfile == "":
    print("Input folder:", args.inputfolder)
    # check backslash
    if args.inputfolder[-1] == "/":
        folder = args.inputfolder
    else:
        folder = args.inputfolder + "/"
    # inputfiles and outputfile
    i3filelist = glob.glob(folder + "LLP*/*.gz")
    outputfile = folder + args.outputfile
elif args.inputfolder == "" and args.inputfile != "":
    # File is given
    print("Input file:", args.inputfile)
    i3filelist = [args.inputfile]
    outputfile = args.outputfile
else:
    print("Please provide either an input folder or an input file. Not neither or both.")
    exit()



# test access to input and output files
for f in i3filelist:
    if not os.access(f,os.R_OK):
        raise Exception('Cannot read from %s'%f)
def test_write(f):
    if f:
        try:
            open(f,'w')
        except OSError:
            raise Exception('Cannot write to %s'%f)
        finally:
            os.remove(f)
test_write(outputfile)

# create tray
tray = I3Tray()

tray.AddModule("I3Reader", "reader", FilenameList=[args.gcdfile] + i3filelist)
tray.AddSegment(base_processing.base_processing, "base",
                simulation=True,
                do_vemcal=False,
                do_icetopslccal=False,
                )

# which keys to remove
remove_keys = ["CalibratedWaveforms",
               "CleanIceTopRawData",
               "CleanRawData",
               "CleanInIceRawData",
               "IceTopRawData",
               "IceTopSLCVEMPulses",
               "IceTopHLCVEMPulses",
               "IceTopHLCPulseInfo",
               "IceTopDSTPulses",
               "TankPulseMergerExcludedTanks",
               "TankPulseMergerExcludedTanksSLC",
               "SLCTankPulses",
               "HLCTankPulses",
               "KeepAllWaveforms",
               "KeepIceTopWaveforms",
               ]

remove_sim_keys = ["I3MCTree",
                   "InIceRawData",
                   "I3MCPulseSeriesMapParticleIDMap",
                   "I3MCPulseSeriesMap",
                   "I3MCPESeriesMap",
                   "I3MCPESeriesMapWithoutNoise",
                   ]

tray.AddModule("Delete", "delete", Keys=remove_keys+remove_sim_keys)

# don't save GCD
tray.AddModule("I3Writer", "writer", filename=outputfile, Streams=[icetray.I3Frame.DAQ,
                                                                        icetray.I3Frame.Physics,
                                                                        icetray.I3Frame.TrayInfo,
                                                                        icetray.I3Frame.Simulation,])

tray.Execute()