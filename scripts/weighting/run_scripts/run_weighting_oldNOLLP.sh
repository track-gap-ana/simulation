#inputfile="/home/axel/i3/new-simprod-test/local-test-no-photon-muongun-info/LLPSimulation.DarkLeptonicScalar.mass-110.0.eps-3e-05.bias-1000000.0.nevents-1.i3.gz"
#countfile="/home/axel/i3/new-simprod-test/local-test-no-photon-muongun-info/llp_counter.json"



inputfile="/home/axel/i3/LLP-data/NO_LLP_DarkLeptonicScalar.mass-999.eps-1.nevents-10000_ene_1e2_1e4_gap_0_231213.201260714/LLPSimulation.201260714.0_fullycontained/LLPSimulation.DarkLeptonicScalar.mass-999.eps-1.nevents-100.i3.gz"
countfile="/home/axel/i3/LLP-data/NO_LLP_DarkLeptonicScalar.mass-999.eps-1.nevents-10000_ene_1e2_1e4_gap_0_231213.201260714/LLPSimulation.201260714.0_fullycontained/llp_counter.json"

python reweight_llp_sim.py --inputfile $inputfile --countfile $countfile --output no_llp_weighted.i3.gz -ws 1e15