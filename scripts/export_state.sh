#!/bin/bash

INI_FILE=$1
STAGE=$2
SECRETS_JSON=$3
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

# Handle secrets
if [ -n "$SECRETS_JSON" ]; then
    echo "Setting secrets..."
    for key in $(echo $SECRETS_JSON | jq -r 'keys[]'); do
        value=$(echo $SECRETS_JSON | jq -r ".${key}")
        case $PLATFORM in
        'github')
            # Handling for GitHub Actions
            echo "$key=$value" >> $GITHUB_ENV
            ;;
        'azdo')
            # Handling for Azure DevOps
            echo "##vso[task.setvariable variable=$key;isSecret=true]$value"
            ;;
        'shell')
            # Default shell export
            export "$key=$value"
            ;;
        esac
    done
fi

# Handle regular variables
while IFS='=' read -r key value; do
    if [[ -n $key && -n $value ]]; then
        case $PLATFORM in
        'github')
            # Handling for GitHub Actions
            echo "$key=$value" >> $GITHUB_ENV
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
