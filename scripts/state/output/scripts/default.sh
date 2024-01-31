#!/bin/bash

# List environment variables
list-variables(){
    echo
    echo "You have access to the following variables:"
    echo "-------------------------------------------"
    env | sort
}

# Function for pre-build steps
pre-build() {
    echo "Running pre-build steps..."
    list-variables
    # Add your pre-build commands here
}

# Function for build steps
build() {
    echo "Running build steps..."
    list-variables
    # Add your build commands here
}

# Function for post-build steps
post-build() {
    echo "Running post-build steps..."
    list-variables
    # Add your post-build commands here
}

# Function for pre-test steps
pre-test() {
    echo "Running pre-test steps..."
    list-variables
    # Add your pre-test commands here
}

# Function for test steps
test() {
    echo "Running test steps..."
    list-variables
    # Add your test commands here
}

# Function for post-test steps
post-test() {
    echo "Running post-test steps..."
    list-variables
    # Add your post-test commands here
}

# Function for pre-deploy steps
pre-deploy() {
    echo "Running pre-deploy steps..."
    list-variables
    # Add your pre-deploy commands here
}

# Function for deploy steps
deploy() {
    echo "Running deploy steps..."
    list-variables
    # Add your deploy commands here
}

# Function for post-deploy steps
post-deploy() {
    echo "Running post-deploy steps..."
    list-variables
    # Add your post-deploy commands here
}

print-scripts() {
    echo
    echo "Other scripting languages are available."
    local json_file="validation.json" # Path to your JSON file
    # Check if jq is installed
    if command -v jq >/dev/null 2>&1; then
        # jq is installed, list the supported script types
        jq -r '.supported.scripts | keys[]' "$json_file"
    else
        # jq is not installed, print a generic message
        echo "Please refer to the documentation for supported script types."
    fi
    echo
    echo "To use a different language, change the 'type' parameter for that stage to one of"
    echo "the supported script types in your pipeline.yml or workflow.yml."
    echo
    echo "To help you get started, this script and examples for other script types can be found at:"
    echo "https://github.com/..."
}

usage(){
    echo
    echo "To use your own script, you can place it in a 'scripts' subfolder next to your pipeline.yml or workflow.yml."
    echo
    echo "Then edit your variables.json and add a PRE_SCRIPT, POST_SCRIPT, APP_BUILD_SCRIPT or APP_DEPLOY_SCRIPT key"
    echo "to either the 'global', 'build', 'test' or 'deploy' section/s and set the value to the name of your script."
    echo
    echo "Don't forget to also change your PRE_SCRIPT_ARGS, POST_SCRIPT_ARGS, APP_BUILD_ARGS and APP_DEPLOY_ARGS accordingly." 
    print-scripts
}

# Main script execution
main() {
    if declare -f "$1" > /dev/null; then
        # Call the function passed as an argument
        "$1"
    else
        echo "Error: '$1' is not a valid function name."
    fi
    usage
}

# Execute the main function
main $1
