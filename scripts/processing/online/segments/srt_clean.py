""" This script does Seeded RT hit cleaning. """

from icecube import icetray
from icecube import dataio
from icecube.icetray import I3Tray
from icecube.icetray import I3Units

from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
from icecube.phys_services.which_split import which_split

import argparse


@icetray.traysegment
def SRTClean(tray, name,
             input_pulses = "SplitInIcePulses",
             output_puslses = "SRTInIcePulses",
             splitname = "InIceSplit",
             ):
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
        OutputHitSeriesMapName = 'SRTInIcePulses',
        STConfigService        = seededRTConfig,
        SeedProcedure          = 'HLCCoreHits',
        NHitsThreshold         = 2,
        MaxNIterations         = 3,
        Streams                = [icetray.I3Frame.Physics],
        If = which_split(split_name=splitname)
    )

