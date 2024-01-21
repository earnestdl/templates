#!/bin/bash

# Usage: ./script.sh [ini_file] [stage] [platform]
# Example: ./script.sh ./variables.ini build_default azdo

INI_FILE=$1
STAGE=$2
PLATFORM=$3

# Function to parse INI file and export variables
parse_ini() {
    awk -F'=' -v stage="[$STAGE]" -v platform="$PLATFORM" '
    $0 == stage {flag=1; next}
    /^[/[]/ && flag {flag=0}
    flag && NF==2 {
        if (platform == "ado") {
            print "echo \"##vso[task.setvariable variable="$1"]"$2"\""
        } else if (platform == "github") {
            print $1"="$2" >> $GITHUB_ENV"
        }
    }
    ' "$INI_FILE"
}

# Export variables
eval $(parse_ini)
