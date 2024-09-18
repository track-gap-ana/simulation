""" computes linefit, spe1st and mpe fit. needs srt cleaned file as input. """

from icecube.icetray import I3Tray
from icecube import icetray, linefit
import icecube.lilliput
import icecube.lilliput.segments


@icetray.traysegment
def TrackReco(tray, name,
              pulses,
              ):
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
