#!/bin/bash

# Usage: ./script.sh [ini_file] [stage] [platform]
# Example: ./script.sh ./variables.ini build_default azdo

INI_FILE=$1
STAGE=$2
PLATFORM=$3

# Function to parse INI file and export variables
parse_ini() {
    awk -F'=' -v stage="[$STAGE]" -v platform="$PLATFORM" '
    $0 ~ stage {flag=1; next}
    /^\[/ && flag {flag=0}
    flag && NF >= 2 {
        # Concatenate the field from the 2nd to the last (to include values with '=' in them)
        value = $2
        for (i = 3; i <= NF; i++) {
            value = value "=" $i
        }
        # Remove leading and trailing spaces from the key and value
        gsub(/^ *| *$/, "", $1)
        gsub(/^ *| *$/, "", value)
        # Print the export command
        print "export " $1"=\""value"\""
        if (platform == "ado") {
            print "echo \"##vso[task.setvariable variable="$1"]"value"\""
        } else if (platform == "github") {
            print $1"=\""value"\" >> $GITHUB_ENV"
        }
    }
    ' "$INI_FILE"
}

# Export variables
eval $(parse_ini)
