#!/bin/bash

INI_FILE=$1
STAGE=$2
OUTPUT_FILE="variables.sh"

echo "Processing state for $STAGE:"
echo "------------------------------------------------------------------------------------"
awk -v stage="\\[$STAGE\\]" '$0 ~ stage,/^\\[/' "$INI_FILE" | sed -e '1d' -e 's/ \?= \?/=/g' > "$OUTPUT_FILE"
cat "$OUTPUT_FILE"
echo "------------------------------------------------------------------------------------"

echo "Exporting variables:"
echo "------------------------------------------------------------------------------------"

while IFS='=' read -r key value; do
    if [[ -n $key && -n $value ]]; then
        # Trim leading and trailing whitespace
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        echo "$key=$value"
        export "$key=$value"
        echo "##vso[task.setvariable variable=$key]$value"
    fi
done < "$OUTPUT_FILE"
