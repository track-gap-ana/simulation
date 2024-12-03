INPUTDIR="/data/sim/IceCube/2020/generated/CORSIKA-in-ice/20904/0198000-0198999/detector"
OUTPUTDIR="/data/user/axelpo/filter-converted-MC/CORSIKA-20904/0198000-0198999/detector/online"

mkdir -p $OUTPUTDIR

GCD="/data/user/axelpo/LLP-at-IceCube/dark-leptonic-scalar-simulation/resources/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz"

counter=0
max_counter=20
for INPUT in "$INPUTDIR"/*.zst
do
    if [[ "$counter" -lt "$max_counter" ]]; then
        echo "$INPUT"
        BASENAME=$(basename $INPUT)
        OUTPUT=$OUTPUTDIR"/online_"$BASENAME
        echo "$OUTPUT"
        python $I3_SRC/online_filterscripts/resources/scripts/PFRaw_to_DST.py -s -i $INPUT -g $GCD -o $OUTPUT
    fi
    counter=$(($counter + 1))
done

