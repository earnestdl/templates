#!/bin/bash

STATE=$1
STAGE=$2
DEPLOY_REGION=""
DEPLOY_REGIONS=()

## ** for local debugging only **
## make sure REGIONS and SECRETS are commented out before pushing changes to git
## in production, these variables will be passed via env param from the deploy template
REGIONS="[ \"east\", \"west\" ]"
SECRETS="{ \"OPENSHIFT_TOKEN_EAST\": \"***\", \"OPENSHIFT_TOKEN_WEST\": \"***\", \"API_KEY\": \"***\" }"

create_empty_json_stage() {
    echo "{
    \"$STAGE\": {
        \"variables\": {},
        \"secrets\": {}
    }
}"
}

update_stage_with_region() {
    local stage="$1"
    local regions_str="$2"  # Regions as a string
    local stage_data="$3"

    # Convert the string of regions to an array
    local regions=($(echo $regions_str | tr -d '[],"' | tr ' ' '\n'))

    # Extract the last token from the stage name
    local region_token=${stage##*_}

    # Check if the region token matches any entry in the regions array
    for region in "${regions[@]}"; do
        if [[ "$region" == "$region_token" ]]; then
            # Update the JSON to include the "regions" attribute
            echo "$stage_data" | jq --arg region "$region" '.["'$stage'"] += {"region": $region}'
            return
        fi
    done

    # If no region matches, return the original JSON
    echo "$stage_data"
}

add_regional_secrets() {
    local stage_data="$1"
    local stage="$2"
    local -n regions_arr="$3"  # Use a nameref for the regions array

    # Extract the region from the stage_data JSON
    local region=$(echo "$stage_data" | jq -r '.["'$stage'"].region // "null"')

    # Check if the region is not null and update accordingly
    if [ "$region" != "null" ]; then
        # Update stage_data JSON by adding CDP_DEPLOY_REGION to variables
        stage_data=$(echo "$stage_data" | jq --arg region "$region" '.["'$stage'"].variables.CDP_DEPLOY_REGION = $region')

        # Update the DEPLOY_REGION global variable
        DEPLOY_REGION=$(echo "$region" | tr '[:lower:]' '[:upper:]')
    fi

    # Reset DEPLOY_REGIONS and update it with uppercase regions
    DEPLOY_REGIONS=()
    for r in "${regions_arr[@]}"; do
        DEPLOY_REGIONS+=("$(echo "$r" | tr '[:lower:]' '[:upper:]')")
    done

    # Return the updated stage_data
    echo "$stage_data"
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

# find stage and create empty json object to add variables and secrets to
stage_data=$(create_empty_json_stage)
echo "Processing data for stage $STAGE:"
echo "---------------------------------------------------"
echo "$stage_data"
echo "---------------------------------------------------"
echo
stage_data=$(update_stage_with_region "$STAGE" "${REGIONS[*]}" "$stage_data")
echo "Validating region for stage $STAGE:"
echo "$stage_data"

# Convert the regions string to an array
readarray -t REGIONS_ARRAY < <(echo $REGIONS | jq -r '.[]')
stage_data=$(add_regional_secrets "$stage_data" "$stage" "REGIONS_ARRAY")
echo "$stage_data"
echo "DEPLOY_REGION: $DEPLOY_REGION"
echo "DEPLOY_REGIONS: ${DEPLOY_REGIONS[*]}"
