#!/bin/bash
set -e
printf "Start time: "; /bin/date
printf "Job is running on node: "; /bin/hostname
printf "Job is running in directory: "; /bin/pwd

eval $(/cvmfs/icecube.opensciencegrid.org/py3-v4.2.1/setup.sh)

# enter icetray and virtual environment, then run script
/data/user/axelpo/i3/icetray-axel/build/env-shell.sh \
/data/user/axelpo/track-gap-ana/simulation/.venv/bin/activate \
python $@

echo "Job complete!"
