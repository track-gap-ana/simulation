import os
import yaml
import json
import shutil

def create_config_dict_from_path(custom_config,
                  default_config="../configs/sim-settings/default.yaml",
                  process_config=True,
                  expand_vars=True, # expand $I3_SRC etc.
                  add_parent_dir=True, # add parent dir to all relevant paths
                  create_PROPOSAL_LLP_config=True, # PROPOSAL config file from parameters
                  use_default_filename=True # use default *.i3.gz filename
                  ):
    # load default config file
    # @TODO: assert it has everything it needs
    if type(default_config) == str:
        with open(default_config) as file:
            params = yaml.safe_load(file)
    
    # load custom config
    with open(custom_config) as file:
        custom_params = yaml.safe_load(file)
    
    params.update(custom_params)
    
    if process_config:
        # call create config dict with dictionaries
        return process_config_dict(params,
                                expand_vars,
                                add_parent_dir,
                                create_PROPOSAL_LLP_config,
                                use_default_filename)
    else:
        return params
    
def process_config_dict(params,
                  expand_vars=True, # expand $I3_SRC etc.
                  add_parent_dir=True, # add parent dir to all relevant paths
                  create_PROPOSAL_LLP_config=True, # PROPOSAL config file from parameters
                  use_default_filename=True # use default *.i3.gz filename
                  ):
    # @TODO: assert params has everything it needs
    
    # cast and assert types
    cast_types(params)
    assert_types(params)

    # expand paths with environment variables
    if expand_vars:
        for key, val in params.items():
            if type(val) == str and "$" in val:
                params[key] = os.path.expandvars(val)

    # Use custom output name?
    if params["outputfile"] == "" or use_default_filename:
        params = add_default_output_name(params)

    # add all relevant paths to same folder?
    directory_path = params["parentdir"] + params["dirname"]
    os.makedirs(directory_path, exist_ok=True)
    if add_parent_dir:
        # add directory path to all files
        params['outputfile']        = directory_path + params['outputfile']
        params['summaryfile']       = directory_path + params['summaryfile']
        params['histogramfilename'] = directory_path + params['histogramfilename']

    if create_PROPOSAL_LLP_config:
        # PROPOSAL parameters
        if params["config_LLP"] is None:
            # if no config file then you must pass all LLP parameters manually
            if (params["mass"] is None) or (params["eps"] is None) or (params["bias"] is None) or (params["LLP-model"] is None):
                raise Exception("If no PROPOSAL LLP config file passed to argparse then you must pass arguments for model, mass, epsilon and bias of the LLP.", "SimulateLLP")
            file = open(params["config_SM"])
            config_json = json.load(file)
            file.close()
            config_json["global"]["llp_enable"]     = True
            config_json["global"]["llp_multiplier"] = params["bias"]
            config_json["global"]["llp_mass"]       = params["mass"]
            config_json["global"]["llp_epsilon"]    = params["eps"]
            config_json["global"]["llp"]            = params["LLP-model"]
        else:
            file = open(params["config_LLP"])
            config_json = json.load(file)
            file.close()
            
        # save new PROPOSAL config file to simulation directory
        if params["config_LLP"] is None:
            params["config_LLP"] = directory_path + "config_LLP.json"
            file = open(params["config_LLP"], "w+")
            file.write(json.dumps(config_json))
            file.close()
        else:
            shutil.copy(params["config_LLP"], directory_path)

    return params


def cast_types(params):
    # @TODO: fill in with all types
    try:
        params["mass"] = float(params["mass"])
        params["eps"] = float(params["eps"])
        params["bias"] = float(params["bias"])
        params["nevents"] = int(params["nevents"])
    except (ValueError, TypeError):
        raise ValueError("Invalid parameter types")

def assert_types(params):
    # @TODO: fill in with all types
    assert isinstance(params["mass"], (float)), "mass should be a numeric value"
    assert isinstance(params["eps"], (float)), "eps should be a numeric value"
    assert isinstance(params["bias"], (float)), "bias should be a numeric value"
    assert isinstance(params["nevents"], int), "nevents should be an integer"

def dump_config_dict(params, outputdir=None, outputname="sim_settings.yaml"):
    # write summary yaml file in directory_path
    if outputdir is None:
        outfile = params["parentdir"] + params["dirname"] + outputname
    else:
        outfile = outputdir + outputname
    with open(outfile, "w") as file:
        yaml.dump(params, file)

def add_default_output_name(params):
    # default filename
    params["outputfile"] = "LLPSimulation."+params["LLP-model"]+\
        ".mass-"+str(params["mass"])+".eps-" + str(params["eps"]) +\
            ".bias-"+str(params["bias"])+".nevents-"+str(params["nevents"])+".i3.gz"
    return params

def bias_recommender(xsec, desired_mean_free_path):
    """ xsec in cm2 and desired_mean_free_path in meters
    """
    # in 1/cm3
    n_oxygen = 6.02214076e23 * 0.92 / 18 # number density of oxygen in ice
    n_hydrogen = 2*n_oxygen              # number density of hydrogen in ice
    n_ice = n_oxygen + n_hydrogen        # number density of ice
    
    # calculate the mean free path of the LLP
    mean_free_path = 1 / (n_ice * xsec) / 100 # convert to meters
    bias =  mean_free_path / desired_mean_free_path
    
    return bias