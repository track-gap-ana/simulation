import os
import yaml
import json
import shutil

def create_config_dict_from_path(custom_config,
                  default_config="../configs/sim-settings/default.yaml",
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
    
    # call create config dict with dictionaries
    return create_config_dict(custom_params,
                              params,
                              expand_vars,
                              add_parent_dir,
                              create_PROPOSAL_LLP_config,
                              use_default_filename)
    
def create_config_dict(custom_params,
                  default_params,
                  expand_vars=True, # expand $I3_SRC etc.
                  add_parent_dir=True, # add parent dir to all relevant paths
                  create_PROPOSAL_LLP_config=True, # PROPOSAL config file from parameters
                  use_default_filename=True # use default *.i3.gz filename
                  ):
    # load default config file
    # @TODO: assert it has everything it needs
    params = default_params.copy()

    # override with custom config
    params.update(custom_params)

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
