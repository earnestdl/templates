#!/bin/bash

STATE=$1
STAGE=$2

## ** for local debugging only **
## make sure REGIONS and SECRETS are commented out before pushing changes to git
## in production, these variables will be passed via env param from the deploy template
REGIONS="[ \"east\", \"west\" ]"
SECRETS="{ \"OPENSHIFT_TOKEN_EAST\": \"***\", \"OPENSHIFT_TOKEN_WEST\": \"***\", \"API_KEY\": \"***\" }"

# Function to find and print stage-specific variables from the state file
find_stage_in_state_file() {
    local state=$1
    local stage=$2
    local processing_stage=false
    local is_secret=false
    declare -A secrets_found

    while IFS= read -r line; do
        if [[ "$line" == "[$stage]" ]]; then
            processing_stage=true
            continue
        fi
        if $processing_stage && [[ "$line" == *"="* ]]; then
            var_name=$(echo "$line" | cut -d= -f1)
            var_value=$(echo "$line" | cut -d= -f2-)

            # Check if the variable is a secret
            if [[ "$var_value" == '$('*')' || "$var_value" == '${{secret.'*'}}' ]]; then
                secrets_found[$var_name]=$var_value
                is_secret=true
            else
                echo "$var_name=$var_value"
            fi
        fi
        if [[ "$line" == *"]" ]] && $processing_stage; then
            break
        fi
    done < "$state"

    # Find possible secret matches
    if [ "${#secrets_found[@]}" -gt 0 ]; then
        echo ""
        echo "${secrets_found[@]}"
        for secret in "${!secrets_found[@]}"; do
            echo "Possible matches for $secret:"
            for key in $(echo "$SECRETS" | jq -r 'keys[]'); do
                if [[ "$key" == "${secret}_"* ]]; then
                    echo "  - $key"
                fi
            done
        done
    fi
}

# Function to set and print the platform
set_platform() {
    if [ -n "$GITHUB_ACTIONS" ]; then
        echo 'github'
    elif [ -n "$AZURE_HTTP_USER_AGENT" ]; then
        echo 'azdo'
    else
        echo 'shell'
    fi
}

# Main script execution
PLATFORM=$(set_platform)
echo "Platform: $PLATFORM"
echo "Regions: $REGIONS"
echo "Secrets: $SECRETS"
echo "Processing state variables for $STAGE on $PLATFORM:"
echo "---------------------------------------------------"
# Extract and print the variables for the specific stage
find_stage_in_state_file "$STATE" "$STAGE"
