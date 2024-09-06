""" LLP MuonGun weights will be off due to initializing MuonGun with infinite muons (1e8). This scripts recomputes correct weights. """

from icecube import icetray, dataio, dataclasses
from icecube import MuonGun
from icecube.icetray import I3Tray

import argparse
import json


def ScaleMuonGunWeight(frame, scale):
    if "MuonWeightUnscaled" in frame:
        frame["MuonWeightScaled"] = dataclasses.I3Double(frame["MuonWeightUnscaled"].value*scale)

def harvest_generators(infiles):
    """
    Harvest serialized generator configurations from a set of I3 files.
    """
    from icecube.icetray.i3logging import log_info as log
    generator = None
    for fname in infiles:
        f = dataio.I3File(fname)
        fr = f.pop_frame(icetray.I3Frame.Stream('S'))
        f.close()
        if fr is not None:
            for k in fr.keys():
                v = fr[k]
                if isinstance(v, MuonGun.GenerationProbability):
                    log('%s: found "%s" (%s)' % (fname, k, type(v).__name__), unit="MuonGun")
                    if generator is None:
                        generator = v
                    else:
                        generator += v
    return generator

class Plotter(icetray.I3Module):
    def __init__(self, ctx):
        icetray.I3Module.__init__(self, ctx)
        pass
    def Configure(self):
        self.scaled_weights = []
        self.unscaled_weights = []
        self.original_weights = []
        self.energies = []
        self.nevents = 0
    def DAQ(self, frame):
        if "MuonWeightScaled" in frame:
            self.scaled_weights.append(frame["MuonWeightScaled"].value)
        if "MuonWeightUnscaled" in frame:
            self.unscaled_weights.append(frame["MuonWeightUnscaled"].value)
        # self.original_weights.append(frame["muongun_weights"].value/10000.)
        # self.original_weights.append(frame["muongun_weights"].value/500.) # @TODO: what is this magic number?
        self.original_weights.append(frame["muongun_weights"].value/(1000.0-352.0))
        self.energies.append(frame["MMCTrackList"][0].particle.energy)
        self.nevents += 1
        
    def Finish(self):
        print("Total number of events:", self.nevents)
        print("Sum of weights:", sum(self.scaled_weights))
        print("Sum of unscaled weights:", sum(self.unscaled_weights))
        print("Sum of original weights:", sum(self.original_weights))
        
        # histogram energy with weights
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Convert lists to numpy arrays
        energies = np.array(self.energies)
        # weights = np.array(self.unscaled_weights)
        # weights = np.array(self.scaled_weights)
        
        original_weights = np.array(self.original_weights)
        scaled_weights = np.array(self.scaled_weights)
        
        # create log bins
        nbins=50
        bins = np.logspace(np.log10(min(self.energies)), np.log10(max(self.energies)), nbins)
        # bins = 100
        
        # Plot histogram
        density=False
        plt.figure()
        plt.hist(energies, bins=bins, weights=original_weights, density=density, label = "original", alpha=0.5)
        plt.hist(energies, bins=bins, weights=scaled_weights, density=density, label = "scaled", alpha=0.5)
        
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel('Energy')
        plt.ylabel('Rate [Hz]')
        plt.legend()
        # plt.title('Scaled')
        
        plt.show()
        
    

###############################################

def add_args(parser):
    """
    Args:
        parser (argparse.ArgumentParser): the command-line parser
    """
    
    parser.add_argument("-o", "--output", action="store",
        type=str, default="weighted_file.i3.gz", dest="outfile",
        help="Output i3 file")

    parser.add_argument("--model", dest="model",
                        default="Hoerandel5_atmod12_SIBYLL",
                        type=str, required=False,
                        help="primary cosmic-ray flux parametrization")
    
    parser.add_argument("-i", "--inputfile", action="store",
        type=str, default="", dest="infile",
        help="Input i3 file(s)  (use comma separated list for multiple files)")
    
    parser.add_argument("-c", "--countfile", action="store",
        type=str, default="", dest="countfile",
        help="Input count json file")
    
    parser.add_argument("-ws", "--weight-scale", dest="weight-scale",
                        default=1e8, type=float, required=False,
                        help="should be 1e8 ('infinity'). number passed to nevents of muongun in full_llp_simulation.py")

# Get params from parser
parser = argparse.ArgumentParser(description="Weight LLP file")
add_args(parser)
params = vars(parser.parse_args())  # dict()
params['infile'] = params['infile'].split(',')

# llp counter dict
with open(params["countfile"], "r") as file:
    # Load the JSON data into a dictionary
    llp_count = json.load(file)
saved_events = llp_count["nevents"]
total_events = llp_count["total"]

# compute scale
# scale = params["weight-scale"] / (total_events - saved_events)
# scale = (params["weight-scale"] - total_events) / params["weight-scale"]
scale = params["weight-scale"] / (total_events)


############### start weighting ###################
model = MuonGun.load_model(params["model"])

if isinstance(params['infile'],list):
    infiles = params['infile']
else:
    infiles = [params['infile']]
    
generator = harvest_generators(infiles)

print("starting tray")
icetray.set_log_level(icetray.I3LogLevel.LOG_INFO)
tray = I3Tray()
tray.Add("I3Reader", filenamelist=infiles)

# weight and scale since muongun thought we simulated 1e8 muons
tray.AddModule('I3MuonGun::WeightCalculatorModule', 'MuonWeightUnscaled', Model=model, Generator=generator)
tray.Add(ScaleMuonGunWeight, scale = scale, streams=[icetray.I3Frame.DAQ])
tray.AddModule(Plotter)
tray.Add("I3Writer", filename=params["outfile"])
tray.Execute()