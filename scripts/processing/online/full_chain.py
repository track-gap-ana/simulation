import icecube
from icecube import icetray, dataio, offline_filterscripts
from icecube.offline_filterscripts import read_superdst_files
from icecube.icetray import I3Tray

from .segments.srt_clean import SRTClean
from .segments.track_reco import TrackReco
from .segments.common_variables import ComputeAllCV

inputfiles = ["", ""]
gcdfile = ''

cleaned_pulses = "SRTInIcePulses"
uncleaned_pulses = "SplitInIcePulses"
subeventstream = "InIceSplit"
reco_particle_name = "MPE_"+cleaned_pulses
bookit = False

tray = I3Tray()
# open files
tray.AddSegment(read_superdst_files.read_superdst_files, 'read_superdst_files',
                input_files = inputfiles,
                input_gcd = gcdfile,
)
# SRT clean pulses
tray.AddSegment(SRTClean, "srt_cleaning", input_pulses=uncleaned_pulses, output_pulses=cleaned_pulses)
# track reconstruction (needed for CV)
tray.AddSegment(TrackReco, "track_reco", pulses=cleaned_pulses)
# compute CommonVariables
tray.AddSegment(ComputeAllCV, "compute_CV",
                 pulses_map_name = cleaned_pulses,
                 reco_particle_name = reco_particle_name,
                 subeventstream = subeventstream,
                 bookit = bookit,
                 )
