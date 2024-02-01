#!/bin/bash

# Function for pre-build steps
pre-build() {
    echo "Running pre-build steps..."
    echo  
    echo  ...
    echo 
    echo "Pre-build steps complete."
}

# Function for build steps
build() {
    echo "Building..."
    echo  
    echo  ...
    echo 
    echo "Build complete."
}

# Function for post-build steps
post-build() {
    echo "Running post-build steps..."
    echo  
    echo  ...
    echo 
    echo "Post-build complete."
}

# Function for pre-test steps
pre-test() {
    echo "Running pre-test steps..."
    echo  
    echo  ...
    echo 
    echo "Pre-test steps complete."
}

# Function for test steps
test() {
    echo "Testing..."
    echo  
    echo  ...
    echo 
    echo "Testing complete."
}

# Function for post-test steps
post-test() {
    echo "Running post-test steps..."
    echo  
    echo  ...
    echo 
    echo "Pre-test steps complete."
}

# Function for pre-deploy steps
pre-deploy() {
    echo "Running pre-deploy steps..."
    echo  
    echo  ...
    echo 
    echo "Pre-deploy steps complete."
}

# Function for deploy steps
deploy() {
    echo "Deploying..."
    echo  
    echo  ...
    echo 
    echo "Deployment complete."
}

# Function for post-deploy steps
post-deploy() {
    echo "Running post-build steps..."
    echo  
    echo  ...
    echo 
    echo "Post-build steps complete."
}

print-scripts() {
    echo

    echo "List of process scripts available:"
    echo "-----------------------------------------------------------------------"
    ls -l ${CDP_PROCESS_SCRIPTS}
    echo 

    echo "List of steps scripts available:"
    echo "-----------------------------------------------------------------------"
    ls -l ${CDP_STEPS_SCRIPTS}
    echo 

    echo "List of state scripts available: (scripts from your repo)"
    echo "-----------------------------------------------------------------------"
    ls -l ${CDP_STATE_SCRIPTS}
    echo 

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
