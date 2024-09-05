cd ../

inputfile="/home/axel/i3/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-150000.0_ene_2000.0_15000.0_gap_100.0_240602.210981234/LLPSimulation.DarkLeptonicScalar.mass-110.0.eps-3e-05.bias-1000000.0.nevents-500.i3.gz"
outputfile="BaseLLPSimulation.i3.gz"
gcdfile="/home/axel/i3/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz"

python online_base_processing.py --inputfile $inputfile --outputfile $outputfile --gcdfile $gcdfile

cd run_scripts/