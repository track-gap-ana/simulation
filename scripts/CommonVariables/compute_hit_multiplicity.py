import icecube
from icecube import icetray, dataclasses, dataio
from icecube.icetray import I3Tray
from icecube.common_variables import hit_multiplicity

# filename
filename = "/data/user/axelpo/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-150000.0_ene_2000.0_15000.0_gap_100.0_240602.210981234/base_processed.i3.gz"
gcdfile = "/data/user/axelpo/LLP-at-IceCube/dark-leptonic-scalar-simulation/resources/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz"
outputname = "test_hit_multiplicity.i3.gz"

# setitings
pulses_map_name    = 'InIceDSTPulses'

# tray
tray = I3Tray()
tray.AddModule("I3Reader", "reader",
               FilenameList = [gcdfile, filename]
              )

# direct hits
tray.AddSegment(hit_multiplicity.I3HitMultiplicityCalculatorSegment, 'hm',
    PulseSeriesMapName                = pulses_map_name,
    OutputI3HitMultiplicityValuesName = 'HitMultiplicityValues',
    BookIt                            = True
)

# writer
tray.AddModule("I3Writer", "writer", filename = outputname)

# execute
tray.Execute(10)