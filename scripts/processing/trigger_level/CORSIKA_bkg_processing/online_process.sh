
INPUT="/data/sim/IceCube/2020/generated/CORSIKA-in-ice/20904/0198000-0198999/detector/IC86.2020_corsika.020904.198000.i3.zst"

OUTPUT="online_IC86.2020_corsika.020904.198000.i3.zst"

GCD="/data/user/axelpo/LLP-at-IceCube/dark-leptonic-scalar-simulation/resources/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz"

python $I3_SRC/online_filterscripts/resources/scripts/PFRaw_to_DST.py -s -i $INPUT -g $GCD -o $OUTPUT