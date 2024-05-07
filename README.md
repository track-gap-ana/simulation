@TODO: update

Scripts for simulating long lived particle at IceCube.

## IMPORTANT REQUIREMENT: custom PROPOSAL

* To simulate LLPs you need to build a version of icetray which contains a **custom version of PROPOSAL**.
* Custom version found on at (branch since forks are not allowed): https://github.com/icecube/icetray/tree/axelpo/main/PROPOSAL (@TODO: maybe we can pull request this into the main branch?)
* The modified PROPOSAL version is explained [here](#custom-proposal)

> **NOTE:** Once the simulation is done, you can analyze the MC set with the official icetray builds. No new frame object types, I3Particles, etc. are added. There is no LLP inside the `I3MCTree`, only the daughter products (SM particles). All LLP information (like gap length, production/decay vertices, etc.) is kept in a `dataclasses.I3MapStringDouble()` called `frame["LLPInfo"]`. This is intentional so people can redo the analysis steps without the custom icetray build. Most simulated LLP MC sets are found at `/data/user/axelpo/LLP-data/`.

# Simulate LLP

The LLP simulation chain follows closely the [simprod-scripts](https://github.com/icecube/icetray/tree/main/simprod-scripts) for atmospheric muons.

You can create a full LLP simulation simply by entering an icetray environment with the custom PROPOSAL version and running:
```bash
python SimulateLLP.py \
 --nevents 10000 \
 --seed 123 \
 --RunID 12345 \
 --UseGPUs \
 --gcdfile $PATHTOGCD \
 --no-natural-rate \
 --min_LLP_length 100 \
 --model Hoerandel5_atmod12_SIBYLL \
 --gamma 2 \
 --offset 700 \
 --emin 1e2 \
 --emax 1e4 \
 --mass 0.115 \
 --eps 5e-5 \
 --bias 3e9 \
 --LLP-model DarkLeptonicScalar \
 --parentdirectory /data/user/axelpo/LLP-data/test-folder \
 --outputfile LLPSimulation.DLS.mass-0.115.eps-5e-5.nevents-10000.i3.gz \
```
There are more options you can use and not all options provided above are necessary. In practice the simulation is run on NPX through [condor](#condor).

## Standard simulation chain
The standard atmospheric muon simulation chain in IceCube is

1. Generation (`MuonGun`)
2. Propagation (`PROPOSAL`)
3. Photon Propagation (`ppc` or `CLSim`)
4. Detector response and triggering (`PMT`, `DomLauncher`, `TriggerSim`)

To simulate long lived particles produced from exotic muon bremsstrahlung we only need to modify the muon propagation, as described in [section below](#custom-proposal).

## LLP simulation chain

The script for simulating LLP is `SimulateLLP.py`, which does everything from generation to trigger simulation. It was created using standard [simprod-scripts](https://github.com/icecube/icetray/tree/main/simprod-scripts) segments, except for the custom muon propagation segment. This is found in `PropagateMuonsLLP.py`, which uses a custom I3PropagatorService found in `I3PropagatorServicePROPOSAL_LLP.py`.

1. Generation (`MuonGun`)
2. Propagation with LLP (custom `PROPOSAL`)
    * Use segment `PropagateMuonsLLP()`
    * Check for nice LLP event, otherwise throw away
3. Photon Propagation (`ppc` or `CLSim`)
4. Detector response and triggering (`PMT`, `DomLauncher`, `TriggerSim`)

### PropagateMuonsLLP segment
In `SimulateLLP.py` you find:
```python
  ### PROPOSAL WITH LLP INTERACTION ###
  tray.AddSegment(PropagateMuonsLLP,
                  "propagator",
                  RandomService          = tray.context["I3RandomService"],
                  InputMCTreeName        = "I3MCTree_preMuonProp",
                  OutputMCTreeName       = "I3MCTree",
                  PROPOSAL_config_SM     = params["config_SM"],
                  PROPOSAL_config_LLP    = params["config_LLP"],
                  OnlySaveLLPEvents      = params["OnlySaveLLPEvents"],
                  only_one_LLP           = params["only_one_LLP"],
                  nevents                = params["nevents"],
                  gcdfile                = params["gcdfile"],
                  both_prod_decay_inside = params["both_prod_decay_inside"],
                  min_LLP_length         = params["min_LLP_length"],
                 )
```

You need to pass two PROPOSAL configs, one without LLP and one with LLP. You can choose to switch to normal PROPOSAL propagator after LLP production with the flag `only_one_LLP` (true by default) since it's unrealistic with two LLPs in the same event. To determine what counts as an LLP event worth saving, you choose `min_LLP_length` (track gap length) and whether both vertices in detector volume with `both_prod_decay_inside`. `OnlySaveLLPEvents` means we throw away muons that didn't produce LLP (default true).

## How does the custom PROPOSAL work? <a name="custom-proposal"></a> 

The functionality of PROPOSAL remains the same except the addition of a new "energy loss" interaction: [LLPInteraction](https://github.com/icecube/icetray/blob/axelpo/main/PROPOSAL/public/PROPOSAL/crossection/parametrization/LLPInteraction.h)

The new LLP interaction is treated like any other stochastic energy loss in PROPOSAL like bremsstrahlung, pair production, etc., except that it kills the muon if it takes place. When PROPOSAL decides for the LLP interaction to take place, it executes the following steps (see function `double Sector::Propagate(double distance)` https://github.com/icecube/icetray/blob/axelpo/main/PROPOSAL/private/PROPOSAL/sector/Sector.cxx#L557).

1. Sample propagated distance until decay for the LLP.
    * Sample time until decay in the LLP rest frame from an exponential distribution.
    * Boost to the lab frame and multiply by the speed of light -> distance travelled.
2.Create vector of daughter particles
    * One lepton at interaction point
    * Two leptons at decay point
3. Set time, energy, position and direction of daughter particles.
    * Energy distribution of the particles from the differential production cross section and decay width of the LLP.
    * Assume all particles collinear with the initial muon.
4. Kill initial muon and push daughter particles to output (which will be further propagated)

### PROPOSAL json config with LLP parameters
* PROPOSAL json config set the LLP parameters model, mass, epsilon and multiplier.
* The LLP interaction is extremely rare. To save resources, we multiply (bias) the interaction cross section by orders of magnitude.

Example snippet from [resources/config_DLS.json](https://github.com/axel-ponten/LLP-at-IceCube/blob/main/dark-leptonic-scalar-simulation/resources/config_DLS.json)

```json
"llp"              : "DarkLeptonicScalar",
"llp_multiplier"   : 2e9,
"llp_mass"         : 130,
"llp_epsilon"      : 5e-6,
```
### IMPORTANT: MMCTrackList effects

> @TODO: can we fix this by removing the extra MMCTrack during simulation? Or is it useful later and we should keep it?
> 
Since the initial muon is killed at production, and if the decay products contain a new muon, the MMCTrackList will contain two tracks, one from the original atmospheric muon from MuonGun, and the second one from the decay muon of the LLP. ***Beware of this when doing weighting etc.***. One easy fix is to copy the MMCTrackList in your tray and then remove the "fake" MMCTrack before adding the module that does the weighting etc. Example here: https://github.com/axel-ponten/LLP-at-IceCube/blob/main/dark-leptonic-scalar-simulation/weight-LLP-events/weight-LLP-events.py#L10 

## Using HTCondor to simulate on the NPX <a name="condor"></a>
* In practice we always produce LLP MC sets on the NPX grid.
* Scripts for submitting found in https://github.com/axel-ponten/LLP-at-IceCube/tree/main/dark-leptonic-scalar-simulation/condor.

The script `ExecuteSimulation.sh` defines config for the simulation (jobs, events per job, model details, muon spectrum, etc.) and submits the jobs. It will create a new condor execution directory where it copies relevant scripts and submits. Particularly it copies the submit template (`condor/condor_submit_template/FullSimulationLLP_template_v2.sub`) and updates config choices in there.

To submit, log into the submit nodes (e.g. `ssh axelpo@submit.icecube.wisc.edu`), and then run
```bash
# go to the condor folder in this repo
cd /data/user/axelpo/LLP-at-IceCube/dark-leptonic-scalar-simulation/condor
# submit jobs. make sure to update config first
source ExecuteSimulation.sh
```

There's also scripts with the suffix `_NoLLP`. This is just used to create a muongun MC set without LLP production, in order to check that the simulation chain works like it should.

## Filtering LLP simulation to L1 and L2
This repo contains copies from [filterscripts](https://github.com/icecube/icetray/tree/main/filterscripts) in the main icetray repo. Need some modified versions to save certain frame keys like "LLPInfo".

1. Simulate online filter (level 1) with SimulateFiltering.py. Added LLPInfo to saved frames in SimulateFilter.py (the default script from i3 repo does not have it, of course).

2. Simulate level 2 using process.py

3. In practice trigger to L2 is done with the script `/data/user/axelpo/LLP-data/runL1L2.sh` or `/data/user/axelpo/LLP-data/condor-filtering` (submit `runL1L2.sh` on the grid) since condor LLP simulation jobs spits out many .i3 files and we want to run it on all of them simultaneously.

# filtering-analysis
* This folder has some scripts to inspect what happens to LLP simulation between trigger and filtering.
* Includes a sanity check of apparent randomness in L2 filtering. This was found to be due to minbias filter.

# spectrum-at-detector-boundary
* spectrum-at-detector-boundary contains some scripts characterising spectrum of atmospheric muons at the detector boundary, both for L2 and trigger. This is unrelated to LLP simulation, only used to obtain single muon spectrum at the detector.

# weight-LLP-events
@TODO: update this
* Contains script to weight the initial muongun spectrum used in LLP simulation. Does not weight according to bias of LLP cross section etc.
