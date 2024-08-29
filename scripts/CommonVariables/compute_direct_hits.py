import icecube
import icecube.icetray as icetray
from icecube import icetray, dataclasses, dataio
from icecube.icetray import I3Tray
from icecube.common_variables import direct_hits

# filename
filename = "/data/user/vparrish/llp_ana/offline/output/earlyLibra_10E3/220824/full/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-500000.0_ene_200.0_15000.0_gap_50.0_240722.213638022/earlyLibra_10E3_full_offline_preprocess_08222024_earlyLeo_full_online_preprocess_08192024_LLPSimulation.DarkLeptonicScalar.mass-110.0.eps-3e-05.bias-1000000.0.nevents-50_21466947_214962476.i3.gz"
gcdfile = "/data/user/axelpo/LLP-at-IceCube/dark-leptonic-scalar-simulation/resources/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz"
outputname = "test_direct_hits.i3.gz"

# setitings
pulses_map_name    = 'CleanedInIcePulses'
reco_particle_name = 'PoleMuonLlhFit'
subeventstreams = ["InIceSplit"]

dh_defs = direct_hits.get_default_definitions()

print('Calculating direct hits for "%s" pulses and "%s" reco particle, using '\
      'these direct hits definitions:'%(pulses_map_name, reco_particle_name))
for dh_def in dh_defs:
    print(dh_def)

# tray
tray = I3Tray()
tray.AddModule("I3Reader", "reader",
               FilenameList = [gcdfile, filename]
              )

# direct hits
tray.AddSegment(direct_hits.I3DirectHitsCalculatorSegment, 'dh',
    DirectHitsDefinitionSeries       = dh_defs,
    PulseSeriesMapName               = pulses_map_name,
    ParticleName                     = reco_particle_name,
    OutputI3DirectHitsValuesBaseName = reco_particle_name+'DirectHits',
    BookIt                           = False,
    SubEventStreams                  = ["InIceSplit"]
)

# writer
tray.Add("I3Writer", "writer", filename = outputname,)

# writer
# tray.Add("I3Writer", "writer", filename = outputname,
#                Streams = [icetray.I3Frame.TrayInfo, icetray.I3Frame.Simulation,
#                         icetray.I3Frame.DAQ, icetray.I3Frame.Physics],
#               DropOrphanStreams=[icetray.I3Frame.Geometry,
#             icetray.I3Frame.Calibration, icetray.I3Frame.DetectorStatus])

# execute
tray.Execute(50)