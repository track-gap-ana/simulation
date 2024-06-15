import pandas as pd
import argparse

# create argparse for input and output files
parser = argparse.ArgumentParser()
parser.add_argument("--mass")
parser.add_argument("--eps")
args = parser.parse_args()

mass = float(args.mass)
eps = float(args.eps)

bias_file = "bias_recommendations.csv"

df = pd.read_csv(bias_file)

# get row with current mass
row = df[df["mass"] == mass]

bias = row["rec_bias"].item() / (eps*eps*1.0)

print("Mass {} and eps {} has recommended bias:\n{:.2e}".format(mass, eps, bias))