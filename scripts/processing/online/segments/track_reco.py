""" computes linefit, spe1st and mpe fit. needs srt cleaned file as input. """

from icecube.icetray import I3Tray
from icecube import icetray, linefit
import icecube.lilliput
import icecube.lilliput.segments


from icecube.phys_services.which_split import which_split

@icetray.traysegment
def TrackReco(tray, name,
              pulses,
              splitname="InIceSplit",
              ):
    ##################################################################
    # Run improved Linefit
    ##################################################################
    fitname_linefit = "linefit_"+pulses
    tray.AddSegment(linefit.simple,
                    "linefit_improved",
                    inputResponse = pulses,
                    fitName = fitname_linefit,
                    If = which_split(split_name=splitname))

    ##################################################################
    # Run SPE1st
    ##################################################################
    fitname_spe = "SPE1st_"+pulses
    tray.Add(icecube.lilliput.segments.I3SinglePandelFitter,
            fitname=fitname_spe,
            domllh="SPE1st",
            pulses=pulses,
            seeds=[fitname_linefit],
            If = which_split(split_name=splitname))

    ##################################################################
    # Run MPE
    ##################################################################
    fitname_mpe = "MPE_"+pulses
    tray.Add(icecube.lilliput.segments.I3SinglePandelFitter,
            fitname=fitname_mpe,
            domllh="MPE",
            pulses=pulses,
            seeds=[fitname_spe],
            If = which_split(split_name=splitname))
