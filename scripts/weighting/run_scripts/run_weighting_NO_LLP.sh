cd ../

folder="/home/axel/i3/LLP-data/NO_LLP_DarkLeptonicScalar.mass-110.eps-3e-05.nevents-10000.0_ene_200.0_10000.0_gap_50.0_240905.215501287/LLPSimulation.215501287.0/"

inputfile=$folder"LLPSimulation.DarkLeptonicScalar.mass-110.0.eps-3e-05.bias--1.0.nevents-1000.i3.gz"
countfile=$folder"llp_counter.json"

python reweight_llp_sim.py --inputfile $inputfile --countfile $countfile --output no_llp_weighted.i3.gz

cd run_scripts