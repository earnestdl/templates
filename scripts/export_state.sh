#!/bin/bash

INI_FILE=$1
STAGE=$2
OUTPUT_FILE="variables.sh"

# Detecting platform
if [ -n "$GITHUB_ACTIONS" ]; then
    PLATFORM='github'
elif [ -n "$AZURE_HTTP_USER_AGENT" ]; then
    PLATFORM='azdo'
else
    PLATFORM='shell'
fi

echo "Processing state for $STAGE on $PLATFORM:"
echo "---------------------------------------------------"
awk -v RS='' "/\\[$STAGE\\]/" "$INI_FILE" > "$OUTPUT_FILE"
while IFS='=' read -r key value; do
    if [[ -n $key && -n $value ]]; then
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        echo "$key=$value"
        
        case $PLATFORM in
        'github')
            # Handling for GitHub Actions
            echo "::set-env name=$key::$value"
            ;;
        'azdo')
            # Handling for Azure DevOps
            export "$key=$value"
            echo "##vso[task.setvariable variable=$key]$value"
            ;;
        'shell')
            # Default shell export
            export "$key=$value"
            ;;
        esac
    fi
done < "$OUTPUT_FILE"
