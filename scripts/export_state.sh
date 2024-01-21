#!/bin/bash

INI_FILE=$1
STAGE=$2
OUTPUT_FILE=statevars.sh

echo Current state:
echo ------------------------------------------------------------------------------------
awk -v stage="$STAGE" -v RS='' '/\[build_'stage'\]/' "$BUILD_SOURCESDIRECTORY/variables/state.ini"
echo ------------------------------------------------------------------------------------

# TODO THIS
# Read each line from the input file
while IFS='=' read -r key value; do
    # Trim leading and trailing whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)
    
    # Write the formatted line to the output file
    echo "export $key=$value && echo ##vso[task.setvariable variable=$key]$value" >> "$OUTPUT_FILE"
done < "$INPUT_FILE"

# Make the output file executable
chmod +x "$OUTPUT_FILE"



echo Exporting state variables for $STAGE on $PLATFORM
awk -v stage="$STAGE" -v RS='' '/\[build_'stage'\]/' "$BUILD_SOURCESDIRECTORY/variables/state.ini" > $OUTPUT_FILE
cat $OUTPUT_FILE
sed -i -e "1d" $OUTPUT_FILE
source $OUTPUT_FILE
echo Completed exporting state file

echo System Environment Variables:
echo ------------------------------------------------------------------------------------
env | sort