import icecube
import icecube.icetray as icetray
from icecube import icetray, dataclasses, dataio, phys_services, hdfwriter
from icecube.phys_services.which_split import which_split
from icecube.icetray import I3Tray, I3Units
from icecube.common_variables import direct_hits, hit_multiplicity, track_characteristics, hit_statistics, time_characteristics
import argparse

# argument parser
parser = argparse.ArgumentParser(description='Compute common variables and save them to an HDF5 file.')
parser.add_argument('--filename', type=str, help='Path to the input file. Comma-separated list of files is allowed.')
parser.add_argument('--gcdfile', type=str, help='Path to the GCD file')
parser.add_argument('--hdf_filename', type=str, default='all_CV.hdf5', help='Name of the output HDF5 file')
parser.add_argument('--pulses_map_name', type=str, default='CleanedInIcePulses', help='Name of the pulses map')
parser.add_argument('--reco_particle_name', type=str, default='PoleMuonLlhFit', help='Name of the reconstructed particle')
parser.add_argument('--subeventstream', type=str, default='InIceSplit', help='Name of the subevent stream')
parser.add_argument('--bookit', action='store_true', help='Flag to enable booking')

args = parser.parse_args()

# filename is a comma-separated list of files
filename = args.filename
filename_list = filename.split(',')

gcdfile = args.gcdfile
hdf_filename = args.hdf_filename
pulses_map_name = args.pulses_map_name
reco_particle_name = args.reco_particle_name
subeventstream = args.subeventstream
bookit = args.bookit

tableio_keys_to_book = []

# tray
tray = I3Tray()
tray.AddModule("I3Reader", "reader",
               FilenameList = [gcdfile] + filename_list,
)

##### DIRECT HITS #####
dh_defs = direct_hits.get_default_definitions()

print('Calculating direct hits for "%s" pulses and "%s" reco particle, using '\
      'these direct hits definitions:'%(pulses_map_name, reco_particle_name))
for dh_def in dh_defs:
    print(dh_def)

tableio_keys_to_book +=\
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
tableio_keys_to_book +=\
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

tableio_keys_to_book +=\
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

tableio_keys_to_book +=\
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

tableio_keys_to_book +=\
tray.AddSegment(hit_statistics.I3HitStatisticsCalculatorSegment, 'hs',
    PulseSeriesMapName              = pulses_map_name,
    OutputI3HitStatisticsValuesName = 'HitStatisticsValues',
    BookIt                          = bookit,
    COGBookRefFrame                 = dataclasses.converters.I3PositionConverter.BookRefFrame.Sph,
    If = which_split(subeventstream),
)

print("Len of tableio_keys_to_book: ", len(tableio_keys_to_book))
print("tableio_keys_to_book: ")
[print(key) for key in tableio_keys_to_book]
print("Writing %s to HDF5 file: %s" % (tableio_keys_to_book, hdf_filename))
tray.AddSegment(hdfwriter.I3HDFWriter, 'hdfwriter',
    Keys            = tableio_keys_to_book,
    SubEventStreams = [subeventstream],
    Output          = hdf_filename
)

# execute
tray.Execute()