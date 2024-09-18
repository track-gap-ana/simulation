cd ../

folder="/home/axel/i3/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-500000.0_ene_200.0_15000.0_gap_50.0_240722.213638022/"
nfiles=-1 # all files

python plot_llp_spectrum.py --inputfolder $folder --nfiles $nfiles

cd run_scripts/