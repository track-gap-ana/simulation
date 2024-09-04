import icecube
import icecube.icetray as icetray
from icecube import icetray, dataclasses, dataio, phys_services
from icecube.phys_services.which_split import which_split
from icecube.icetray import I3Tray, I3Units
from icecube.common_variables import direct_hits, hit_multiplicity, track_characteristics, hit_statistics, time_characteristics

# filename
filename = "/home/axel/i3/LLP-data/offline_processed/earlyLibra_10E3_full_offline_preprocess_08222024_earlyLeo_full_online_preprocess_08192024_LLPSimulation.DarkLeptonicScalar.mass-110.0.eps-3e-05.bias-1000000.0.nevents-50_21466947_214962476.i3.gz"
gcdfile = "/home/axel/i3/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz"

outputname = "test_all_CV.i3.gz"

# settings
pulses_map_name    = 'CleanedInIcePulses'
reco_particle_name = 'PoleMuonLlhFit'
subeventstream = "InIceSplit"
bookit = False

# tray
tray = I3Tray()
tray.AddModule("I3Reader", "reader",
               FilenameList = [gcdfile, filename]
)

##### DIRECT HITS #####
dh_defs = direct_hits.get_default_definitions()

print('Calculating direct hits for "%s" pulses and "%s" reco particle, using '\
      'these direct hits definitions:'%(pulses_map_name, reco_particle_name))
for dh_def in dh_defs:
    print(dh_def)

tray.AddSegment(direct_hits.I3DirectHitsCalculatorSegment, 'dh',
    DirectHitsDefinitionSeries       = dh_defs,
    PulseSeriesMapName               = pulses_map_name,
    ParticleName                     = reco_particle_name,
    OutputI3DirectHitsValuesBaseName = reco_particle_name+'DirectHits',
    BookIt                           = bookit,
    If = which_split(subeventstream),
)

##### HIT MULTIPLICITY #####
print('Calculating hit multiplicity for "%s" pulses' % (pulses_map_name))
tray.AddSegment(hit_multiplicity.I3HitMultiplicityCalculatorSegment, 'hm',
    PulseSeriesMapName                = pulses_map_name,
    OutputI3HitMultiplicityValuesName = 'HitMultiplicityValues',
    BookIt                            = bookit,
    If = which_split(subeventstream),
)

##### TIME CHARACTERISTICS #####
time_cylinder_radius = 150.*I3Units.m

print('Calculating time characteristics for "%s" '\
        'pulses' %\
        (pulses_map_name))

tray.AddSegment(time_characteristics.I3TimeCharacteristicsCalculatorSegment, 'timec',
    PulseSeriesMapName                     = pulses_map_name,
    OutputI3TimeCharacteristicsValuesName = reco_particle_name+'TimeCharacteristics',
    BookIt                                 = bookit,
    If = which_split(subeventstream),
)

##### TRACK CHARACTERISTICS #####
track_cylinder_radius = 150.*I3Units.m

print('Calculating track characteristics for "%s" '\
        'pulses and "%s" reco particle within the "%fm" track cylinder '\
        'radius.'%\
        (pulses_map_name, reco_particle_name, track_cylinder_radius))

tray.AddSegment(track_characteristics.I3TrackCharacteristicsCalculatorSegment, 'trackc',
    PulseSeriesMapName                     = pulses_map_name,
    ParticleName                           = reco_particle_name,
    OutputI3TrackCharacteristicsValuesName = reco_particle_name+'TrackCharacteristics',
    TrackCylinderRadius                    = track_cylinder_radius,
    BookIt                                 = bookit,
    If = which_split(subeventstream),
)

##### HIT STATISTICS #####
print('Calculating hit statistics for "%s" pulses' % (pulses_map_name))
tray.AddSegment(hit_statistics.I3HitStatisticsCalculatorSegment, 'hs',
    PulseSeriesMapName              = pulses_map_name,
    OutputI3HitStatisticsValuesName = 'HitStatisticsValues',
    BookIt                          = bookit,
    COGBookRefFrame                 = dataclasses.converters.I3PositionConverter.BookRefFrame.Sph,
    If = which_split(subeventstream),
)


# writer, will add 8 new frame objects from the common variables
# overwrites PoleMuonLlhFitDirectHitsBaseC which was already in frame, and its not the same!! maybe different pulse series?
tray.Add("I3Writer", "writer", filename = outputname,
               Streams = [icetray.I3Frame.TrayInfo, icetray.I3Frame.Simulation,
                        icetray.I3Frame.DAQ, icetray.I3Frame.Physics],
              DropOrphanStreams=[icetray.I3Frame.Geometry,
            icetray.I3Frame.Calibration, icetray.I3Frame.DetectorStatus])

# execute
tray.Execute()