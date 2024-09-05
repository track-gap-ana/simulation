""" This script does Seeded RT hit cleaning. """

from icecube import icetray
from icecube import dataio
from icecube.icetray import I3Tray
from icecube.icetray import I3Units

from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
from icecube.phys_services.which_split import which_split

import argparse

# create argparse for input and output files
parser = argparse.ArgumentParser()
parser.add_argument("--inputfile", "-i", help="input i3 file", default="")
parser.add_argument("--outputfile", "-o", help="output i3 file after cleaning", default="srt_cleaned.i3.gz")
parser.add_argument("--gcdfile", "-g", help="GCD file", default="/data/user/axelpo/LLP-at-IceCube/dark-leptonic-scalar-simulation/resources/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz")

args = parser.parse_args()
print("Convert using:\ninputfile {}:\noutputfile {}:\ngcdfile {}".format(args.inputfile, args.outputfile, args.gcdfile))

# Create a SeededRT configuration object with the standard RT settings.
seededRTConfig = I3DOMLinkSeededRTConfigurationService(
                     ic_ic_RTRadius              = 150.0*I3Units.m,
                     ic_ic_RTTime                = 1000.0*I3Units.ns,
                     treat_string_36_as_deepcore = False,
                     useDustlayerCorrection      = False,
                     allowSelfCoincidence        = True
                 )

# configure tray
tray = I3Tray()
print("Configuring tray")
# read
tray.AddModule("I3Reader", "reader", FilenameList = [args.gcdfile, args.inputfile])

# pulse clean
tray.AddModule('I3SeededRTCleaning_RecoPulseMask_Module', 'North_seededrt',
    InputHitSeriesMapName  = 'SplitInIcePulses',
    OutputHitSeriesMapName = 'SRTInIcePulses',
    STConfigService        = seededRTConfig,
    SeedProcedure          = 'HLCCoreHits',
    NHitsThreshold         = 2,
    MaxNIterations         = 3,
    Streams                = [icetray.I3Frame.Physics],
    If = which_split(split_name='InIceSplit')
)


# don't save GCD
tray.AddModule("I3Writer", "writer", filename=args.outputfile, Streams=[icetray.I3Frame.DAQ,
                                                                        icetray.I3Frame.Physics,
                                                                        icetray.I3Frame.TrayInfo,
                                                                        icetray.I3Frame.Simulation,])

# run tray
print("Executing tray")
tray.Execute()
