
inputfolder="/home/axel/i3/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-500000.0_ene_200.0_15000.0_gap_50.0_240722.213638022/LLPSimulation.213638022.0/"

inputfile=$inputfolder"LLPSimulation.DarkLeptonicScalar.mass-110.0.eps-3e-05.bias-1000000.0.nevents-500.i3.gz"
countfile=$inputfolder"llp_counter.json"

python reweight_llp_sim.py --inputfile $inputfile --countfile $countfile --output weighted_allE.i3.gz