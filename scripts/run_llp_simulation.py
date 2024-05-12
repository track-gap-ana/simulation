import icecube
from icecube import icetray
from icecube.simprod.util.simprodtray import RunI3Tray

import llp_simulation
import llp_simulation.utils
import llp_simulation.full_llp_simulation
import argparse

# Create the argument parser
parser = argparse.ArgumentParser(description='LLP Simulation')
parser.add_argument('--default-config', dest="default-config",
                    type=str, default="../configs/sim-settings/default.yaml", help='Path to the default config file')
parser.add_argument('--custom-config', dest="custom-config",
                    type=str, default="../configs/sim-settings/custom.yaml", help='Path to the custom config file')
args = vars(parser.parse_args()) # dict

# create config dictionary
params = llp_simulation.utils.create_config_dict_from_path(args["custom-config"],
                                                           args["default-config"],
                                                           process_config=True)

# dump the config dictionary to a yaml file in the output directory
llp_simulation.utils.dump_config_dict(params)

# suppress warnings from PROPOSAL LLP integration
#icetray.set_log_level(icetray.I3LogLevel.LOG_FATAL)

# Execute Tray
summary = RunI3Tray(params, llp_simulation.full_llp_simulation.configure_tray, "MuonGunGenerator",
                    summaryfile=params['summaryfile'],
                    summaryin=icecube.dataclasses.I3MapStringDouble(),
                    outputfile=params['outputfile'],
                    seed=params['seed'],
                    nstreams=params['nproc'],
                    streamnum=params['procnum'],
                    usegslrng=params['usegslrng'])
