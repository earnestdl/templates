#!/bin/bash

STATE_FILE=$1
STAGE=$2

echo STATE_FILE=$1
echo STAGE=$2
echo REGIONS=$REGIONS
echo SECRETS=$SECRETS

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
    # Check if the line contains "=" (indicating a variable)
    if [[ "$line" == *"="* ]]; then
        var_name=$(echo "$line" | cut -d= -f1)
        var_value=$(echo "$line" | cut -d= -f2-)
        
        # Check if it's a secret by comparing with the SECRETS parameter
        secrets_json=$(echo "$SECRETS" | jq -r '.')
        is_secret=false
        if [ -n "$secrets_json" ]; then
            for key in $(echo "$secrets_json" | jq -r 'keys[]'); do
                value=$(echo "$secrets_json" | jq -r ".${key}")
                if [ "$var_value" == "$value" ]; then
                    is_secret=true
                    break
                fi
            done
        fi
        
        # Check if it's a region-specific variable and remove the region
        if [ -n "$REGIONS" ] && [[ "$var_name" == *"_EAST" || "$var_name" == *"_WEST" ]]; then
            var_name=$(echo "$var_name" | sed -E "s/_(EAST|WEST)//")
        fi
        
        if $is_secret; then
            # It's a secret
            echo "Secret: $var_name"
            # Depending on the platform, set the secret
            case $PLATFORM in
            'github')
                echo "::add-mask::$var_value"  # Mask the secret
                echo "echo \"$var_name=\$var_value\" >> \$GITHUB_ENV"  # Set as GitHub variable
                ;;
            'azdo')
                echo "##vso[task.setvariable variable=$var_name;issecret=true]$var_value"  # Set as AzDO secret variable
                ;;
            'shell')
                # Default shell export
                export "$var_name=$var_value"
                ;;
            esac
        else
            # Regular variable
            echo "Variable: $var_name=$var_value"
            case $PLATFORM in
            'github')
                echo "echo \"$var_name=\$var_value\" >> \$GITHUB_ENV"  # Set as GitHub variable
                ;;
            'azdo')
                echo "##vso[task.setvariable variable=$var_name]$var_value"  # Set as AzDO variable
                ;;
            'shell')
                # Default shell export
                export "$var_name=$var_value"
                ;;
            esac
        fi
    fi
done < "$STATE_FILE"
