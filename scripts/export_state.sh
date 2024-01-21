#!/bin/bash

INI_FILE=$1
STAGE=$2
OUTPUT_FILE="variables.sh"

echo "Processing state for $STAGE:"
echo "---------------------------------------------------"
awk -v RS='' "/\\[$STAGE\\]/" "$INI_FILE" > "$OUTPUT_FILE"
while IFS='=' read -r key value; do
    if [[ -n $key && -n $value ]]; then
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        echo "$key=$value"
        export "$key=$value"
        echo "##vso[task.setvariable variable=$key]$value"
    fi
done < "$OUTPUT_FILE"
