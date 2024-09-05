cd ../

folder="/data/user/axelpo/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-150000.0_ene_2000.0_15000.0_gap_100.0_240602.210981234/"
inputfile=$folder"base_processed.i3.gz"
outputfile=$folder"srt_cleaned.i3.gz"

python srt_pulse_cleaning.py --inputfile $inputfile --outputfile $outputfile

cd run_scripts/