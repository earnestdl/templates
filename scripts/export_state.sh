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

# Process secrets from SECRETS
for key in $(echo "$SECRETS" | jq -r 'keys[]'); do
    secret_value=$(echo "$SECRETS" | jq -r ".${key}")
    secrets_array[$key]=$secret_value
done

# Read the state file and process variables
while IFS= read -r line; do
    if [[ "$line" == *"="* ]]; then
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
done < "$STATE_FILE"

echo "Processing state secrets for $STAGE on $PLATFORM:"
echo "---------------------------------------------------"
echo "Setting secrets..."

# Process OPENSHIFT_TOKEN based on region
openshift_token_key="OPENSHIFT_TOKEN_$REGION"
if [[ -v secrets_array[$openshift_token_key] ]]; then
    echo "OPENSHIFT_TOKEN=***"
fi

# Process other secrets
for key in "${!secrets_array[@]}"; do
    if [[ "$key" != "$openshift_token_key" ]]; then
        echo "$key=***"
    fi
done
