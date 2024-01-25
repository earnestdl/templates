#!/bin/bash

# Function for job A processing
job_a() {
    local data="$1"
    local input_a="$2"
    # Merge data from input_a into the existing data
    echo "$data" | jq --argjson inputA "$input_a" '. += $inputA'
}

# Function for job B processing
job_b() {
    local data="$1"
    local input_b="$2"
    # Merge data from input_b into the existing data
    echo "$data" | jq --argjson inputB "$input_b" '. += $inputB'
}

# Function for validating data
validate_data() {
    local data="$1"
    local validation_data="$2"
    # Compare the processed data with the validation data
    if jq --exit-status --null-input --argjson data1 "$data" --argjson data2 "$validation_data" '$data1 == $data2'; then
        echo "Validation successful: Data matches the validation data."
    else
        echo "Validation failed: Data does not match the validation data."
    fi
}

# Main script starts here

# Create an empty JSON object
processed_data='{}'
echo "Initial data: $processed_data"

# Read inputs from files
input_a=$(<input_a.json)
input_b=$(<input_b.json)
validation_data=$(<validation_data.json)

# Process data through job A
processed_data=$(job_a "$processed_data" "$input_a")
echo "After job A: $processed_data"

# Process data through job B
processed_data=$(job_b "$processed_data" "$input_b")
echo "After job B: $processed_data"

# Validate data
validate_data "$processed_data" "$validation_data"
