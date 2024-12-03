
folder="/data/user/axelpo/LLP-data/DarkLeptonicScalar.mass-110.eps-1e-05.nevents-2500.0_ene_200.0_25000.0_gap_5.0_241129.220626103/"

python check_sim_set.py -f "$folder" --remove-bad

python online_base_processing.py --inputfolder $folder

inputfile=$folder"base_processed.i3.gz"
outputfile=$folder"srt_cleaned.i3.gz"

python srt_pulse_cleaning.py --inputfile $inputfile --outputfile $outputfile


#
#folder="/data/user/axelpo/LLP-data/DarkLeptonicScalar.mass-110.eps-3e-05.nevents-500000.0_ene_200.0_15000.0_gap_50.0_240917.215984659/"
#
#python checks/check_sim_set.py -f "$folder" --remove-bad
#
#python online_base_processing.py --inputfolder $folder
#
#inputfile=$folder"base_processed.i3.gz"
#outputfile=$folder"srt_cleaned.i3.gz"
#
#python srt_pulse_cleaning.py --inputfile $inputfile --outputfile $outputfile
