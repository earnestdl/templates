#!/bin/bash

STATE_FILE=$1
STAGE=$2

echo STATE_FILE=$1
echo STAGE=$2
echo REGIONS=$REGIONS
echo SECRETS=$SECRETS

# Extract the region from the STAGE variable
REGION=$(echo "$STAGE" | awk -F'_' '{print $NF}')

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

# Read the state file and process variables and secrets
while IFS= read -r line; do
    if [[ "$line" == *"="* ]]; then
        var_name=$(echo "$line" | cut -d= -f1)
        var_value=$(echo "$line" | cut -d= -f2-)

        # Check if the variable is in the SECRETS list
        is_secret=false
        for key in $(echo "$SECRETS" | jq -r 'keys[]'); do
            if [[ "$var_name" == "$key" || "$var_name" == "${key}_${REGION}" ]]; then
                is_secret=true
                var_value=$(echo "$SECRETS" | jq -r ".${key}")
                break
            fi
        done

        # Exporting the variable/secret
        if $is_secret; then
            echo "Secret: $var_name"
            case $PLATFORM in
            'github')
                echo "::add-mask::$var_value"
                echo "echo \"$var_name=\$var_value\" >> \$GITHUB_ENV"
                ;;
            'azdo')
                echo "##vso[task.setvariable variable=$var_name;issecret=true]$var_value"
                ;;
            'shell')
                export "$var_name=$var_value"
                ;;
            esac
        else
            echo "Variable: $var_name=$var_value"
            case $PLATFORM in
            'github')
                echo "echo \"$var_name=\$var_value\" >> \$GITHUB_ENV"
                ;;
            'azdo')
                echo "##vso[task.setvariable variable=$var_name]$var_value"
                ;;
            'shell')
                export "$var_name=$var_value"
                ;;
            esac
        fi
    fi
done < "$STATE_FILE"
