

from icecube.icetray import I3Tray
from icecube import icetray, MuonGun

from llp_simulation.weighting import weighting

@icetray.traysegment
def LLPWeighting(tray, name,
                 inputfiles,
                 i3_json_map,
                 model="Hoerandel5_atmod12_SIBYLL"
                 ):
    """ weights the LLP events """
    
    # model
    model = MuonGun.load_model(model)
    
    # get tot_mu_generated_list
    json_files = []
    for i3_file in inputfiles:
        json_files.append(i3_json_map[i3_file])
    tot_mu_generated_list = weighting.get_tot_mu_generated_list(json_files, key="muongun:ncalls")
    # get muongun generator
    generator = weighting.harvest_rescaled_generators(inputfiles, tot_mu_generated_list)
    print("Generator:", generator)
    print("Total event:", generator.total_events)
    
    # do the weighting
    tray.AddModule('I3MuonGun::WeightCalculatorModule', 'MuonWeight', Model=model, Generator=generator)
