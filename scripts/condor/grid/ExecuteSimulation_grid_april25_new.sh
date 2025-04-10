# environment params
export REPODIR=/data/user/axelpo/track-gap-ana/simulation/
export VENV=$REPODIR".venv/bin/activate"
# new icetray env with ftp3 holeice
export ICETRAYENV=/data/user/axelpo/i3/icetray-axel/build/env-shell.sh

# datadir to store sim
export DATADIR=/data/user/axelpo/LLP-data/grid/test_grid/

# config files
export GRIDTOPDIR=$REPODIR"configs/sim-settings/grid/online_LLP_event_rate_april25/"
export DEFAULTSIMCONFIGFILE=$GRIDTOPDIR"default_grid_april25.yaml"
export GRIDDIR=$GRIDTOPDIR"grid/"

# job file
export PYTHONSCRIPT=$REPODIR"scripts/condor/llp_sim_job.py"
export LOGSCRATCHDIR=/scratch/axelpo/
export OUTPUTDIR=/data/user/axelpo/condor-logs/output/
export ERRORDIR=/data/user/axelpo/condor-logs/error/
export CURRENTDATE=`date +%y%m%d`

# computing parameters
export NCPUS=1
export MEMORY=8GB
export DISK=2GB
export NGPUS=1

# simulation parameters
export NJOBS=2
export NEVENTS=100
export DATASETID=289

#skript used for condor
export CONDORSCRIPT=$(pwd)"/templates/FullSimulationLLP_grid_template.sub"
export JOBFILETEMPLATE=$REPODIR"scripts/condor/templates/job_template.sh"

for file in $GRIDDIR*; do

    echo $file
    export CURRENTBASENAME=$(basename $file .yaml)
    echo $CURRENTBASENAME

    # #create exepath to avoid condor incident
    export EXEDIR=$(pwd)"/condor_exe_dirs/condor-$(date +%Y%m%d-%H%M%S)/"$CURRENTBASENAME
    echo $EXEDIR
    mkdir -p $EXEDIR

    export SIMCONFIGFILE=$file

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
        -e 's#<datadir>#'$DATADIR'#g' \
        $CONDORSCRIPT > "$EXEDIR/condor.submit";

    # transform job script
    sed -e 's#<icetrayenv>#'$ICETRAYENV'#g' \
        -e 's#<venv>#'$VENV'#g' \
        $JOBFILETEMPLATE > "$EXEDIR/job.sh";

    #call condor skript
    #echo "CALLING CONDOR SERVICE:"
    cd $EXEDIR
    condor_submit condor.submit

    #back to original directory
    #echo "back to the original directory"
    cd -

done


