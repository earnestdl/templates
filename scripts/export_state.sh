#!/bin/bash

INI_FILE=$1
STAGE=$2
OUTPUT_FILE="variables.sh"

echo Current state:
echo ------------------------------------------------------------------------------------
awk -v RS= -v stage="[${STAGE}]" '$0 ~ stage' "$INI_FILE"
echo ------------------------------------------------------------------------------------

# Extract the relevant section using awk and format it
awk -v RS= -v stage="[${STAGE}]" '$0 ~ stage' "$INI_FILE" > "$OUTPUT_FILE"
sed -i -e '1d' -e 's/ \?= \?/=/g' "$OUTPUT_FILE"

# Read and export variables
while IFS='=' read -r key value; do
    if [[ -n $key && -n $value ]]; then
        # Trim leading and trailing whitespace
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        
        # Export variable to current shell and to AzDO environment
        export "$key=$value"
        echo "##vso[task.setvariable variable=$key]$value"
    fi
done < "$OUTPUT_FILE"

echo System environment variables:
echo ------------------------------------------------------------------------------------
env | sort
