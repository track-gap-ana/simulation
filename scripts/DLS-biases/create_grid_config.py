import pandas as pd
import os
import yaml

# # create argparse for input and output files
# masses = [0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0]
# epilons = [0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0]

grid_points = [(0.11, 5e-5), (0.11, 1e-4), (0.115, 5e-5), (0.115, 1e-3), (0.11, 5e-3),]


bias_file = "bias_recommendations_5lambda_700GeV.csv"
repodir="/data/user/axelpo/track-gap-ana/simulation"
config_dir = os.path.join(repodir, "configs/sim-settings/grid/")
grid_dir = os.path.join(config_dir, "grid_test")
# create grid_dir if it does not exist, parents ok
if not os.path.exists(grid_dir):
    os.makedirs(grid_dir)

df = pd.read_csv(bias_file)

# get row with current mass
for mass, eps in grid_points:
    eps = eps
    row = df[df["mass"] == mass]
    bias = row["rec_bias"].item() / (eps*eps*1.0)

    settings_dict = {"mass": mass*1000.0, # GeV to MeV
                    "eps": eps,
                    "bias": bias,
    }
    
    filename = "mass_{}_eps_{:.2e}_bias_{:.2e}.yaml".format(mass, eps, bias)
    
    # dump dict to yaml in grid_dir
    with open(os.path.join(grid_dir, filename), "w") as file:
        yaml.dump(settings_dict, file)

    print("Mass {} and eps {:.2e} has recommended bias:\n{:.2e}".format(mass, eps, bias))