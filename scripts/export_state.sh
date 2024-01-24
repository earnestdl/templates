#!/bin/bash

STATE_FILE=$1
STAGE=$2

echo "Processing state variables for $STAGE on $PLATFORM:"
echo "---------------------------------------------------"

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

# Initialize secrets array
declare -A secrets_array

# Convert REGIONS JSON array to bash array
readarray -t regions_array < <(echo "$REGIONS" | jq -r '.[]')

# Process secrets from SECRETS
for key in $(echo "$SECRETS" | jq -r 'keys[]'); do
    secret_value=$(echo "$SECRETS" | jq -r ".${key}")
    secrets_array[$key]=$secret_value
done

# Filter the state file for the relevant stage and process variables
processing_stage=false
while IFS= read -r line; do
    if [[ "$line" == "[$STAGE]" ]]; then
        processing_stage=true
        continue
    fi
    if $processing_stage && [[ "$line" == *"="* ]]; then
        var_name=$(echo "$line" | cut -d= -f1)
        var_value=$(echo "$line" | cut -d= -f2-)

        # Check if the variable is a secret
        if [[ -v secrets_array[$var_name] ]]; then
            # Secret variable
            echo "$var_name=***"
        else
            # Regular variable
            echo "$var_name=$var_value"
        fi
    fi
    if [[ "$line" == *"]" ]] && $processing_stage; then
        break
    fi
done < "$STATE_FILE"

echo "Processing state secrets for $STAGE on $PLATFORM:"
echo "---------------------------------------------------"
echo "Setting secrets..."

# Process secrets considering region specificity
for key in "${!secrets_array[@]}"; do
    # Extract potential region suffix from the key
    key_region="${key##*_}"
    base_key="${key%_*}"

    if [[ " ${regions_array[@]} " =~ " ${key_region} " && "$key_region" == "$REGION" ]]; then
        # Region-specific secret for the current region
        echo "$base_key=***"
    elif [[ ! " ${regions_array[@]} " =~ " ${key_region} " ]]; then
        # Non-region-specific secret
        echo "$key=***"
    fi
done
