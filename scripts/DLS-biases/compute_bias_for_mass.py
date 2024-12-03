""" Computes recommended bias based off mean free path.
    Assumes eps=1. Scale bias -> bias/eps^2 to account for different eps.
    Takes xsec at 1 TeV.
"""

from llp_simulation.utils import bias_recommender
import os
import pandas as pd

# desired mean free path
detector_length = 1000  # meters
desired_mean_free_path = 5 * detector_length  # meters

# open DLS cross sections
path_to_cross_section_tables = "cross_section_tables/"
dirpath = os.path.dirname(__file__)
absolute_path = os.path.join(dirpath, path_to_cross_section_tables)
cross_section_files = os.listdir(absolute_path)

# read xsec and compute recommended bias
bias_dict = {"mass": [], "xsec1tev": [], "rec_bias": []}
for file in cross_section_files:
    # get the mass
    mass = file.split("_")[-1][:-4]
    # open csv to dataframe
    df = pd.read_csv(absolute_path + file, header=None)
    df = df.set_index(0)
    # get the xsec for 1 TeV
    xsec_1tev = df.loc[700].values[0]
    # get recommended bias
    rec_bias = bias_recommender(xsec_1tev, desired_mean_free_path)
    # add to dict
    bias_dict["mass"].append(mass)
    bias_dict["xsec1tev"].append(xsec_1tev)
    bias_dict["rec_bias"].append(rec_bias)

# convert to dataframe
df_bias = pd.DataFrame(bias_dict)
# sort by mass
df_bias = df_bias.sort_values(by="mass")
print(df_bias)
# save df to file
path = os.path.dirname(__file__)
path = os.path.join(path, "bias_recommendations_5lambda_700GeV.csv")
df_bias.to_csv(path, index=False)
