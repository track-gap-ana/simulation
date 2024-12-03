# environment params
ICETRAYENV=/data/user/axelpo/i3/icetray-main/build/env-shell.sh

# input files
INPUTFOLDER="/data/user/axelpo/LLP-data/DarkLeptonicScalar.mass-110.eps-1e-05.nevents-1000000.0_ene_200.0_25000.0_gap_5.0_241129.220629158/"

# job file
SCRIPTFOLDER="/data/user/axelpo/track-gap-ana/simulation/scripts/processing/trigger_level/"
CHECKSCRIPT=$SCRIPTFOLDER"check_sim_set.py"
PROCSCRIPT=$SCRIPTFOLDER"online_base_processing.py"
SRTSCRIPT=$SCRIPTFOLDER"srt_pulse_cleaning.py"

LOGSCRATCHDIR=/scratch/axelpo/
OUTPUTDIR=/data/user/axelpo/condor-logs/output/
ERRORDIR=/data/user/axelpo/condor-logs/error/
CURRENTDATE=`date +%y%m%d`

# computing parameters
NCPUS=1
MEMORY=8GB
DISK=2GB
NGPUS=1

#script used for condor
CONDORSCRIPT=$(pwd)"/templates/CheckProcSRT_template.sub"
JOBFILETEMPLATE=$(pwd)"/templates/job_template.sh"

#create exepath to avoid condor incident (many submissions at the same time)
EXEDIR=$(pwd)"/condor_exe_dirs/condor-$(date +%Y%m%d-%H%M%S)"
mkdir $EXEDIR

# transform sub script
sed -e 's#<logscratchdir>#'$LOGSCRATCHDIR'#g' \
    -e 's#<outputdir>#'$OUTPUTDIR'#g' \
    -e 's#<errordir>#'$ERRORDIR'#g' \
    -e 's#<ncpus>#'$NCPUS'#g' \
    -e 's#<memory>#'$MEMORY'#g' \
    -e 's#<disk>#'$DISK'#g' \
    -e 's#<ngpus>#'$NGPUS'#g' \
    -e 's#<checkscript>#'$CHECKSCRIPT'#g' \
    -e 's#<procscript>#'$PROCSCRIPT'#g' \
    -e 's#<srtscript>#'$SRTSCRIPT'#g' \
    $CONDORSCRIPT > "$EXEDIR/condor.submit";


# transform job script
sed -e 's#<icetrayenv>#'$ICETRAYENV'#g' \
    -e 's#<checkscript>#'$CHECKSCRIPT'#g' \
    -e 's#<procscript>#'$PROCSCRIPT'#g' \
    -e 's#<srtscript>#'$SRTSCRIPT'#g' \
    -e 's#<inputfolder>#'$INPUTFOLDER'#g' \
    $JOBFILETEMPLATE > "$EXEDIR/job.sh";

#call condor skript
echo "CALLING CONDOR SERVICE:"
cd $EXEDIR
condor_submit condor.submit

#back to original directory
echo "back to the original directory"
cd -
