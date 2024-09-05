#!/usr/bin/env python3
""" computes linefit, spe1st and mpe fit. needs srt cleaned file as input. """

import argparse
from icecube.icetray import I3Tray
from icecube import icetray, dataclasses, dataio, phys_services, linefit, DomTools
import icecube.lilliput
import icecube.lilliput.segments

parser = argparse.ArgumentParser(description='Track Reco Chain Axel')
parser.add_argument('--inputfile', type=str, help='Path to the data file')
parser.add_argument('--outputfile', type=str, help='Path to the outputfile')
parser.add_argument('--pulses', type=str, help='Pulses to use', default="SRTInIcePulses")
parser.add_argument('--gcdfile', type=str, help='Path to the GCD file', default="/home/axel/i3/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz")
parser.add_argument('--nevents', type=int, help='Number of events to process', default=-1)

args = parser.parse_args()

inputfile = args.inputfile
gcdfile = args.gcdfile
outputfile = args.outputfile
pulses = args.pulses
nevents = args.nevents

# datafiles
# inputfile = "/home/axel/i3/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-150000.0_ene_2000.0_15000.0_gap_100.0_240602.210981234/srt_cleaned.i3.gz"

filenamelist = [
    gcdfile,
    inputfile,
]

tray = I3Tray()
tray.AddModule("I3Reader", "reader")(
    ("filenamelist", filenamelist),
)

##################################################################
# Run improved Linefit
##################################################################
fitname_linefit = "linefit_"+pulses
tray.AddSegment(linefit.simple,
                "linefit_improved",
                inputResponse = pulses,
                fitName = fitname_linefit)

##################################################################
# Run SPE1st
##################################################################
fitname_spe = "SPE1st_"+pulses
tray.Add(icecube.lilliput.segments.I3SinglePandelFitter,
         fitname=fitname_spe,
         domllh="SPE1st",
         pulses=pulses,
         seeds=[fitname_linefit])

##################################################################
# Run MPE
##################################################################
fitname_mpe = "MPE_"+pulses
tray.Add(icecube.lilliput.segments.I3SinglePandelFitter,
         fitname=fitname_mpe,
         domllh="MPE",
         pulses=pulses,
         seeds=[fitname_spe])

##################################################################
# Write
##################################################################
tray.AddModule("I3Writer","writer",
    FileName = outputfile,
)

if nevents < 0:
    tray.Execute()
else:
    tray.Execute(nevents)
