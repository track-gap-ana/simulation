#!/usr/bin/env python3

"""This script illustrates the use of the IceTray segments defined in
`lilliput`.
"""
import os

import icecube
import icecube.icetray
import icecube.dataclasses
import icecube.dataio
import icecube.linefit
import icecube.gulliver
import icecube.gulliver_modules
import icecube.gulliver_modules.iceopt
import icecube.lilliput
import icecube.lilliput.segments
from icecube.icetray import I3Tray

# datafiles
filename = "/home/axel/i3/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-150000.0_ene_2000.0_15000.0_gap_100.0_240602.210981234/srt_cleaned.i3.gz"
gcdfile = "/home/axel/i3/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz"

filenamelist = [
    gcdfile,
    filename,
]

# settings
srtpulses = "SRTInIcePulses"
nevents = 100

scriptname = "trysegments"

opts = icecube.gulliver_modules.iceopt.IceTrayScriptOptions(
    name=scriptname, definput=filename, defgcd=gcdfile, defverbose=True,
    defnevents=nevents, moreopts=True)

opts.add_option("-N", "--nchminimum",
                default=10,
                dest="nchminimum",
                type="int",
                help="threshold value for nch")
opts.add_option("-S", "--nstrminimum",
                default=4,
                dest="nstrminimum",
                type="int",
                help="threshold value for nstr")
opts.add_option("-P", "--pulsename",
                default=srtpulses,
                dest="recopulses",
                help="name of cleaned pulsemap to use for reconstruction")

opts.parse()
srtpulses = opts.recopulses  # type: ignore[attr-defined]

# ----IceTray------------------------------------------------------------------
tray = I3Tray()

# ----Services-----------------------------------------------------------------
# tray.Add("I3XMLSummaryServiceFactory",
#          OutputFilename=opts.xmlfile)

# ----Modules------------------------------------------------------------------
tray.Add("I3Reader",
         FilenameList=opts.infiles)


def multiplicity_cut(frame):
    if srtpulses not in frame:
        return False
    pulsemap = icecube.dataclasses.I3RecoPulseSeriesMap.from_frame(
        frame, srtpulses)
    nch = len(pulsemap)
    nstr = len(set([dom.string for dom in pulsemap.keys()]))
    return nch >= opts.nchminimum and nstr >= opts.nstrminimum  # type: ignore[attr-defined]


tray.Add(multiplicity_cut)

tray.Add("I3LineFit",
         Name="linefit",
         InputRecoPulses=srtpulses,
         AmpWeightPower=1.)

tray.Add(icecube.lilliput.segments.I3SinglePandelFitter,
         fitname="spe",
         domllh="SPE1st",
         pulses=srtpulses,
         seeds=["linefit"])

tray.Add(icecube.lilliput.segments.I3IterativePandelFitter,
         fitname="spe4",
         pulses=srtpulses,
         seeds=["linefit"])

tray.Add(icecube.lilliput.segments.I3IterativePandelFitter,
         fitname="spe8",
         pulses=srtpulses,
         seeds=["linefit"],
         n_iterations=8)

tray.Add(icecube.lilliput.segments.I3SinglePandelFitter,
         fitname="mpe",
         domllh="MPE",
         pulses=srtpulses,
         seeds=["spe8"])

tray.Add("I3Writer",
         Streams=[icecube.icetray.I3Frame.Physics],
         FileName=opts.outfile)

tray.Add("I3EventCounter",
         NEvents=opts.nevents,
         CounterStep=100)

# ----Execute------------------------------------------------------------------
tray.Execute()