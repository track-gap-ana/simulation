#!/bin/bash
set -e
printf "Start time: "; /bin/date
printf "Job is running on node: "; /bin/hostname
printf "Job is running in directory: "; /bin/pwd

eval $(/cvmfs/icecube.opensciencegrid.org/py3-v4.3.0/setup.sh)
export PYTHONPATH=""

folder="<inputfolder>"
inputfile=$folder"base_processed.i3.gz"
outputfile=$folder"srt_cleaned.i3.gz"

# enter icetray and virtual environment, then run script
<icetrayenv> << EOF
python <checkscript> -f $folder --remove-bad
python <procscript> --inputfolder $folder
python <srtscript> --inputfile $inputfile --outputfile $outputfile
EOF

echo "Job complete!"
