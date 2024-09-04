cd ../

input="/home/axel/i3/LLP-data/NO_LLP.DarkLeptonicScalar.mass-130.eps-5e-6.nevents-5000_230919.196721202/L2.i3.gz"
# file_list=$(ls "$folder" | grep '\.gz$' | tr '\n' ',' | sed 's/,$//')
# echo "$file_list"

# # filename1="/home/axel/i3/LLP-data/offline_processed/earlyLibra_10E3_full_offline_preprocess_08222024_earlyLeo_full_online_preprocess_08192024_LLPSimulation.DarkLeptonicScalar.mass-110.0.eps-3e-05.bias-1000000.0.nevents-50_21466947_214962476.i3.gz"

# filenamelist=$file_list
gcdfile="/home/axel/i3/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz"
output="bkg_muon_L2.hdf5"
pulseseries="SRTInIcePulses"
line_fit="PoleMuonLlhFit"
split="InIceSplit"

python compute_all_CV_to_hdf5.py \
    --input $input \
    --gcdfile $gcdfile \
    --hdf_filename $output \
    --pulses_map_name $pulseseries \
    --reco_particle_name $line_fit \
    --subeventstream $split \
    --bookit

cd run_scripts/