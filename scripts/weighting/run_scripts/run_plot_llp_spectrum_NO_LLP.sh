cd ../

folder="/home/axel/i3/LLP-data/NO_LLP_DarkLeptonicScalar.mass-110.eps-3e-05.nevents-50000.0_ene_50.0_10000.0_gap_50.0_240906.215525070/"
nfiles=-1 # all files

python plot_llp_spectrum.py --inputfolder $folder --nfiles $nfiles

cd run_scripts/