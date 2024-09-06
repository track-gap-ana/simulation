#inputfile="/home/axel/i3/new-simprod-test/local-test-no-photon-muongun-info/LLPSimulation.DarkLeptonicScalar.mass-110.0.eps-3e-05.bias-1000000.0.nevents-1.i3.gz"
#countfile="/home/axel/i3/new-simprod-test/local-test-no-photon-muongun-info/llp_counter.json"

inputfile="/home/axel/i3/new-simprod-test/local-test-no-LLP/LLPSimulation.DarkLeptonicScalar.mass-110.0.eps-3e-05.bias--1.0.nevents-10000.i3.gz"
countfile="/home/axel/i3/new-simprod-test/local-test-no-LLP/llp_counter.json"

python reweight_llp_sim.py --inputfile $inputfile --countfile $countfile --output no_llp_weighted.i3.gz