import argparse
import yaml

import icecube
from icecube import icetray
from icecube.simprod.util.simprodtray import RunI3Tray

import llp_simulation
import llp_simulation.utils
import llp_simulation.full_llp_simulation

# Create the argument parser
parser = argparse.ArgumentParser(description='LLP condor job simulation')
parser.add_argument('--config-file', dest="config-file",
                    type=str, required=True, help='Path to the custom config file')
parser.add_argument('--default-config-file', dest="default-config-file",
                    type=str, required=True, help='Path to the default config file')
parser.add_argument('--nevents', dest="nevents", type=int, required=True, help='Number of events per job.')
parser.add_argument('--seed', dest="seed", type=int, required=True, help='Seed for simprod')
parser.add_argument('--nproc', dest="nproc", type=int, required=True, help='Number of jobs.')
parser.add_argument('--procnum', dest="procnum", type=int, required=True, help='Job number.')
parser.add_argument('--clusterid', dest="clusterid", type=int, required=True, help='Condor Cluster ID.')
parser.add_argument('--current-date', dest="current-date", type=str, required=True, help='Current date.')
parser.add_argument('--datadir', dest="datadir", type=str, default="/data/user/axelpo/LLP-data/", help='Data directory')
parser.add_argument('--runid', dest="runid", type=int, required=True, help='Run ID.')

args = vars(parser.parse_args()) # dict

# get config dict
with open(args["config-file"], "r") as file:
    custom_config = yaml.load(file, Loader=yaml.FullLoader)
with open(args["default-config-file"], "r") as file:
    default_config = yaml.load(file, Loader=yaml.FullLoader)
# fill customconfig with default config
default_config.update(custom_config)
custom_config = default_config

# override stuff
custom_config["nevents"] = args["nevents"]
custom_config["seed"]    = args["seed"]
custom_config["nproc"]   = args["nproc"]
custom_config["procnum"] = args["procnum"]
custom_config["runid"]   = args["runid"]

# variables for naming
model      = custom_config["LLP-model"]
mass       = str(custom_config["mass"])
eps        = str(custom_config["eps"])
bias       = str(custom_config["bias"])
minlength  = str(custom_config["min_LLP_length"])
nevents    = float(custom_config["nevents"])
njobs      = float(custom_config["nproc"])
fluxemin   = str(custom_config["emin"])
fluxemax   = str(custom_config["emax"])

# create parent directory
datadir = args["datadir"]
simsetdir = "{}.mass-{}.eps-{}.nevents-{}_ene_{}_{}_gap_{}_{}.{}/".format(
    model, mass, eps, str(nevents * njobs), fluxemin, fluxemax, minlength, args["current-date"], args["clusterid"]
)
parentdirectory = datadir + simsetdir
custom_config["parentdir"] = parentdirectory
custom_config["dirname"] = "LLPSimulation." + str(args["clusterid"]) + "." + str(args["procnum"]) + "/"

# add paths, create LLP proposal config, etc.
params = llp_simulation.utils.process_config_dict(custom_config, default_config)

# dump the config dictionary to a yaml file in the output directory
llp_simulation.utils.dump_config_dict(params)

# suppress warnings from PROPOSAL LLP integration
icetray.set_log_level(icetray.I3LogLevel.LOG_NOTICE)
icetray.set_log_level_for_unit("PROPOSAL", icetray.I3LogLevel.LOG_ERROR)

# Execute Tray
summary = RunI3Tray(params, llp_simulation.full_llp_simulation.configure_tray, "LLPSimulation",
                    summaryfile=params['summaryfile'],
                    summaryin=icecube.dataclasses.I3MapStringDouble(),
                    outputfile=params['outputfile'],
                    seed=params['seed'],
                    nstreams=params['nproc'], # removed in commit https://github.com/icecube/icetray/commit/146750ffe132d617d945c4cff6801b28cea2f8d6 
                    streamnum=params['procnum'],
                    usegslrng=params['usegslrng'],
                    )
