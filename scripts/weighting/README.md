Weighting LLP simulation events! Example script is found in plot_llp_spectrum.py. The functionality for retrieving rescaled generators is in llp_simulation.weighting.weighting

# Usage
You need two ordered lists of input .i3 files and summary.json/llp_counter.json files. We use either summary.json with key "muongun:ncall" or llp_counter.json with key "total" to get total number of muons generated to produce that file.

Then harvest generators and rescale them, then call weighting module like normal.

```python
# get infiles and summaryfiles, make sure they are in the same order
infiles = glob.glob(params["infolder"] + "*/LLP*.i3.gz")[:nfiles]
countfiles = glob.glob(params["infolder"] + "*/llp_counter.json")[:nfiles]

############### start weighting ###################
model = MuonGun.load_model(params["model"])

# get total muons generated from summary files
tot_mu_generated_list = weighting.get_tot_mu_generated_list(countfiles, key="total")
# get muongun generator
generator = weighting.harvest_rescaled_generators(infiles, tot_mu_generated_list)

tray = I3Tray()

tray.Add("I3Reader", filenamelist=infiles)
tray.AddModule('I3MuonGun::WeightCalculatorModule', 'MuonWeight', Model=model, Generator=generator)
tray.AddModule(Plotter)
tray.Execute()
```

# incoherent explanation of rescaling weights in LLP simulation
tl;dr: rescale muongun generators by tot_mu_generated / tot_mu_init then weight like normal!!

LLP simulation uses muongun to generate single muons. We don't know in advance how many muons
need to be generated before we reach our desired number of good LLP events.
We therefore pass "infinite" nevents (tot_mu_init, 1e8 in our case) to initialize muongun in simulation.
We then terminate the simulation once we reach desired number of events, 
leaving us with some number tot_mu_generated which is how many muons we ACTUALLY generated.

tot_mu_init is found in the generator object in the I3 files like "generator.total_events".
tot_mu_generated is found in the summary.json files like "muongun:ncall" or in the llp_counter.json files as "total".

The generators found in the simulation frame of the LLP simulation .i3 files contain muongun generator objects,
but they don't "know" that we terminated early.

As such we rescale the generators like generator = generator * tot_mu_generated / tot_mu_init, and then weight like normal.