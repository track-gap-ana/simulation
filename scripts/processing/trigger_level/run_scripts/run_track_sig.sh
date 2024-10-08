cd ../

input="/home/axel/i3/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-500000.0_ene_200.0_15000.0_gap_50.0_240722.213638022/srt_cleaned.i3.gz"
output="/home/axel/i3/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-500000.0_ene_200.0_15000.0_gap_50.0_240722.213638022/track_reco_srt.i3.gz"
gcdfile="/home/axel/i3/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz"
pulses="SRTInIcePulses"

python track_reco_chain.py \
--inputfile $input \
--outputfile $output \
--gcdfile $gcdfile \
--pulses $pulses

cd run_scripts/