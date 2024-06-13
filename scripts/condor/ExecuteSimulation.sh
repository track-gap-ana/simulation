# simulation parameters
export NJOBS=100
export NEVENTS=500
export DATASETID=777

# environment params
export REPODIR=/data/user/axelpo/track-gap-ana/simulation/
export VENV=$REPODIR".venv/bin/activate"
export ICETRAYENV=/data/user/axelpo/i3/icetray-axel/build/env-shell.sh

# config files
export SIMCONFIGFILE=$REPODIR"configs/sim-settings/custom_condor.yaml"
export DEFAULTSIMCONFIGFILE=$REPODIR"configs/sim-settings/default_condor.yaml"

# job file
export PYTHONSCRIPT=$(pwd)/llp_sim_job.py
export LOGSCRATCHDIR=/scratch/axelpo/
export OUTPUTDIR=/data/user/axelpo/condor-logs/output/
export ERRORDIR=/data/user/axelpo/condor-logs/error/
export CURRENTDATE=`date +%y%m%d`

# computing parameters
export NCPUS=1
export MEMORY=8GB
export DISK=2GB
export NGPUS=1

#skript used for condor
export CONDORSCRIPT=$(pwd)"/templates/FullSimulationLLP_template.sub"
export JOBFILETEMPLATE=$(pwd)"/templates/job_template.sh"

#create exepath to avoid condor incident
export EXEDIR=$(pwd)"/condor_exe_dirs/condor-$(date +%Y%m%d-%H%M%S)"
mkdir $EXEDIR

#transform condor script
sed -e 's#<pythonscript>#'$PYTHONSCRIPT'#g' \
    -e 's#<simconfigfile>#'$SIMCONFIGFILE'#g' \
    -e 's#<defaultsimconfigfile>#'$DEFAULTSIMCONFIGFILE'#g' \
    -e 's#<logscratchdir>#'$LOGSCRATCHDIR'#g' \
    -e 's#<outputdir>#'$OUTPUTDIR'#g' \
    -e 's#<errordir>#'$ERRORDIR'#g' \
    -e 's#<ncpus>#'$NCPUS'#g' \
    -e 's#<memory>#'$MEMORY'#g' \
    -e 's#<disk>#'$DISK'#g' \
    -e 's#<ngpus>#'$NGPUS'#g' \
    -e 's#<njobs>#'$NJOBS'#g' \
    -e 's#<currentdate>#'$CURRENTDATE'#g' \
    -e 's#<nevents>#'$NEVENTS'#g' \
    -e 's#<datasetid>#'$DATASETID'#g' \
    $CONDORSCRIPT > "$EXEDIR/condor.submit";

# transform job script
sed -e 's#<icetrayenv>#'$ICETRAYENV'#g' \
    -e 's#<venv>#'$VENV'#g' \
    $JOBFILETEMPLATE > "$EXEDIR/job.sh";

#call condor skript
echo "CALLING CONDOR SERVICE:"
cd $EXEDIR
condor_submit condor.submit

#back to original directory
echo "back to the original directory"
cd -
