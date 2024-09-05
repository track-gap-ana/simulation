""" Script that takes in trigger level file and runs the following:
    - Base processing
    - SRT cleaning
    - Track reco (linefit, SPE1st, MPE)
    """
    
import icecube
import icecube.icetray
from icecube import icetray
from icecube import dataio
from icecube.icetray import I3Tray
import icecube.online_filterscripts.base_segments.base_processing as base_processing
from icecube import linefit
from icecube.icetray import I3Units
import icecube.lilliput
import icecube.lilliput.segments

from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
from icecube.phys_services.which_split import which_split


import argparse
import glob
import os

# create argparse for input and output files
parser = argparse.ArgumentParser()
parser.add_argument("--inputfile", "-i", help="input DAQ i3 file", default="")
parser.add_argument("--inputfolder", "-f", help="input folder with DAQ i3 files", default="")
parser.add_argument('--pulses', type=str, help='Pulses to use', default="SRTInIcePulses")
parser.add_argument("--gcdfile", "-g", help="GCD file", default="/data/user/axelpo/LLP-at-IceCube/dark-leptonic-scalar-simulation/resources/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz")
parser.add_argument("--outputfile", "-o", help="output i3 file after processing", default="example_CV.i3.gz")

args = parser.parse_args()

# variables
pulses = args.pulses

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

##########################################################
# Run Base Processing
##########################################################

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


##########################################################
# Run SRT cleaning
##########################################################

# Create a SeededRT configuration object with the standard RT settings.
seededRTConfig = I3DOMLinkSeededRTConfigurationService(
                     ic_ic_RTRadius              = 150.0*I3Units.m,
                     ic_ic_RTTime                = 1000.0*I3Units.ns,
                     treat_string_36_as_deepcore = False,
                     useDustlayerCorrection      = False,
                     allowSelfCoincidence        = True
                 )

# pulse clean
tray.AddModule('I3SeededRTCleaning_RecoPulseMask_Module', 'North_seededrt',
    InputHitSeriesMapName  = 'SplitInIcePulses',
    OutputHitSeriesMapName = pulses,
    STConfigService        = seededRTConfig,
    SeedProcedure          = 'HLCCoreHits',
    NHitsThreshold         = 2,
    MaxNIterations         = 3,
    Streams                = [icetray.I3Frame.Physics],
    If = which_split(split_name='InIceSplit')
)

##########################################################
# Run track reco
##########################################################

# Run improved Linefit
fitname_linefit = "linefit_"+pulses
tray.AddSegment(linefit.simple,
                "linefit_improved",
                inputResponse = pulses,
                fitName = fitname_linefit)

# Run SPE1st
fitname_spe = "SPE1st_"+pulses
tray.Add(icecube.lilliput.segments.I3SinglePandelFitter,
         fitname=fitname_spe,
         domllh="SPE1st",
         pulses=pulses,
         seeds=[fitname_linefit])

# Run MPE
fitname_mpe = "MPE_"+pulses
tray.Add(icecube.lilliput.segments.I3SinglePandelFitter,
         fitname=fitname_mpe,
         domllh="MPE",
         pulses=pulses,
         seeds=[fitname_spe])

# don't save GCD
tray.AddModule("I3Writer", "writer", filename=outputfile, Streams=[icetray.I3Frame.DAQ,
                                                                        icetray.I3Frame.Physics,
                                                                        icetray.I3Frame.TrayInfo,
                                                                        icetray.I3Frame.Simulation,])

tray.Execute()