#!/bin/bash
set -e
printf "Start time: "; /bin/date
printf "Job is running on node: "; /bin/hostname
printf "Job is running in directory: "; /bin/pwd

eval $(/cvmfs/icecube.opensciencegrid.org/py3-v4.2.1/setup.sh)

# enter icetray and virtual environment, then run script
<icetrayenv> << EOF
<venv>
python $@

EOF

echo "Job complete!"
