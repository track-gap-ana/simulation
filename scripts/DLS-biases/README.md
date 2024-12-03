What bias should be used in the simulation? If too small then we waste resources simulating muons that don't produce LLP, if too large (free mean path same order magnitude as detector) we will get a skewed distribution of LLPs to the front of the detector.

These scripts compute the xsec bias needed to achieve a certain free mean path with respect to the detector length (1 km).

There is a table of total cross sections at different energies (in GeV) for a mass *m* with $\epsilon = 1$ in **cross_section_tables/**. The script compute_bias_for_mass.py will create a .csv with recommended biases $\epsilon = 1$ given some energy (specified in the script) and number of detector lengths as free mean path (number of lambdas).

There's two settings: 10 lambda at 1 TeV and 5 lambda at 700 GeV

Script get_bias.py (10 lambda 1 TeV) and get_bias_5lambda_700GeV.py will return the actual bias to be used in the simulation for a mass and epsilon.

### Simulation Bias Guidelines

Choosing the appropriate bias for the simulation is crucial. A bias that is too small wastes resources by simulating muons that do not produce LLPs. Conversely, a bias that is too large (with a free mean path comparable to the detector's size) results in a skewed distribution of LLPs towards the front of the detector.

These scripts calculate the cross-section bias required to achieve a specific free mean path relative to the detector length (1 km).

In the **cross_section_tables/** directory, you will find a table of total cross sections at various energies (in GeV) for a mass *m* with $\epsilon = 1$. The `compute_bias_for_mass.py` script generates a .csv file with recommended biases for $\epsilon = 1$, given certain muon energy (specified in the script) and the number of detector lengths as the free mean path (number of lambdas).

There are two settings available:
- 10 lambda at 1 TeV
- 5 lambda at 700 GeV

The `get_bias.py` script (for 10 lambda at 1 TeV) and the `get_bias_5lambda_700GeV.py` script will return the actual bias to be used in the simulation for a given mass and epsilon.

You can of course create a new .csv with whatever energy and num. lambda you want.