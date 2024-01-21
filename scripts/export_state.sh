#!/bin/bash
INI_FILE=$1
STAGE=$2
OUTPUT_FILE=statevars.sh

echo Current state:
echo ------------------------------------------------------------------------------------
awk -v stage="$STAGE" -v RS='' '/\[build_'stage'\]/' "$BUILD_SOURCESDIRECTORY/variables/state.ini"
echo ------------------------------------------------------------------------------------

echo Exporting state variables for $STAGE on $PLATFORM
awk -v stage="$STAGE" -v RS='' '/\[build_'stage'\]/' "$BUILD_SOURCESDIRECTORY/variables/state.ini" > $OUTPUT_FILE
cat $OUTPUT_FILE
sed -i -e "1d" $OUTPUT_FILE
source $OUTPUT_FILE
echo Completed exporting state file

echo System Environment Variables:
echo ------------------------------------------------------------------------------------
env | sort