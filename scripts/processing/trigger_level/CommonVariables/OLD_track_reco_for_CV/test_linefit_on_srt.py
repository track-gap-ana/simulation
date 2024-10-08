#!/usr/bin/env python3

#This is a complete example for the improved linefit code.

from icecube.icetray import I3Tray
from icecube import icetray, dataclasses, dataio, phys_services, linefit, DomTools

# datafiles
datafile = "/home/axel/i3/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-150000.0_ene_2000.0_15000.0_gap_100.0_240602.210981234/srt_cleaned.i3.gz"
gcdfile = "/home/axel/i3/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz"

filenamelist = [
    gcdfile,
    datafile,
]

# settings
pulses = "SRTInIcePulses"
nevents = 1000

tray = I3Tray()
tray.AddModule("I3Reader", "reader")(
    ("filenamelist", filenamelist),
)

##################################################################
# Run improved Linefit
##################################################################
#Note that this example illustrates two ways to use this code.  You can use the
#code as tray segment, or as 4 modules.  

#Run as a tray segment 
tray.AddSegment(linefit.simple,"example", inputResponse = pulses, fitName = "linefit_improved")
# 
# #Run as separate modules
# tray.AddModule("DelayCleaning", "DelayCleaning", InputResponse =
# pulses, OutputResponse="Pulses_delay_cleaned")

# tray.AddModule("HuberFit", "HuberFit", Name = "HuberFit", InputRecoPulses =
# "Pulses_delay_cleaned")

# tray.AddModule("Debiasing", "Debiasing", OutputResponse = "debiasedHits",
# InputResponse = "Pulses_delay_cleaned", Seed = "HuberFit")

# tray.AddModule("I3LineFit","linefit_final", Name = "linefit_final",
# InputRecoPulses = "debiasedHits", LeadingEdge= "ALL", AmpWeightPower= 0.0)


#"linefit_final" is the final product of whole series. 
##################################################################
# Write output to file and move to next frame
##################################################################

tray.AddModule("I3Writer","writer")(
    #("Streams",[icetray.I3Frame.Physics]),    
    ("FileName","example_linefit.i3"),
    ("CompressionLevel",0),
)

if nevents < 0:
    tray.Execute()
else:
    tray.Execute(nevents)

