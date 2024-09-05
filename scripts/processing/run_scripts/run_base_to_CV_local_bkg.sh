cd ../

folder="/home/axel/i3/LLP-data/CORSIKA-in-ice-20904/trigger/"

inputfile=$folder"IC86.2020_corsika.020904.000000.i3.zst"
outputfile=$folder"processed/base_IC86.2020_corsika.020904.000000.i3.zst"
srt_outputfile=$folder"processed/srt_IC86.2020_corsika.020904.000000.i3.zst"
track_outputfile=$folder"processed/track_IC86.2020_corsika.020904.000000.i3.zst"
CV_outputfile=$folder"processed/CV_IC86.2020_corsika.020904.000000.i3.zst"
gcdfile="/home/axel/i3/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz"

pulses="SRTInIcePulses"

# base process
python online_base_processing.py --inputfile $inputfile --outputfile $outputfile --gcdfile $gcdfile

# srt clean
python srt_pulse_cleaning.py --inputfile $outputfile --outputfile $srt_outputfile --gcdfile $gcdfile

# track reco
python track_reco_chain.py \
--inputfile $srt_outputfile \
--outputfile $track_outputfile \
--gcdfile $gcdfile \
--pulses $pulses

# common variables
python compute_all_CV.py \
--input $track_outputfile \
--outputfile $CV_outputfile \
--gcdfile $gcdfile \
--pulses_map_name $pulses \
--reco_particle_name "MPE_"$pulses

cd run_scripts/