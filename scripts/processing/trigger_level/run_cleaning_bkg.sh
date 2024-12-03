inputfile="/data/user/axelpo/base-processed-MC/CORSIKA-20904/base_IC86.2020_corsika.020904.198000.i3.zst"
outputfile="/data/user/axelpo/base-processed-MC/CORSIKA-20904/srt_cleaned_IC86.2020_corsika.020904.198000.i3.zst"

python srt_pulse_cleaning.py --inputfile $inputfile --outputfile $outputfile
