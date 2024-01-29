import os
import re
import json
import yaml
import shutil
import argparse

state_file='state.ini'
output_folder='./output'
validation_json='../../variables/state/validation.json'

def find_yaml_with_variables(variables_file):
    directory = os.path.dirname(variables_file) or os.getcwd()
    variables_filename = os.path.basename(variables_file)
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if file.endswith('.yml') or file.endswith('.yaml'):
            with open(file_path, 'r') as yaml_file:
                try:
                    content = yaml.safe_load(yaml_file)
                    if variables_filename in str(content):
                        log("INFO",f"YAML file found in: {file_path}")
                        return content
                    else:
                        log("ERROR",f"YAML file not found.")
                except yaml.YAMLError as exc:
                    log("ERROR", f"Error parsing YAML file {file_path}")
    return None

def get_validation_data():
    with open(validation_json, 'r') as file:
        validation_data = json.load(file)

    return validation_data

def get_variables_data(variables_file):
    with open(variables_file, 'r') as file:
        variables_data = json.load(file)

    return variables_data

def get_default_regions(deploy_file_path):
    with open(deploy_file_path, 'r') as file:
        deploy_data = yaml.safe_load(file)
    
    deploy_parameters = deploy_data.get('parameters', [])
    default_regions = next((param for param in deploy_parameters if param['name'] == 'regions'), {}).get('default', [])
    
    return default_regions

def validate_stage_consistency(pipeline_data, variables_data):
    # Initialize an empty set for missing stages
    missing_in_variables = set()

    # Iterate through each stage in pipeline_data
    for stage_id in pipeline_data:
        if stage_id != "global":
            # Split the stage name to handle region-specific names
            parts = stage_id.split('_')
            stage_type = parts[0]  # The type of stage (e.g., 'build', 'deploy', 'test')
            stage_name = parts[1]  # The base stage name (e.g., 'app', 'dev')
            region = parts[2] if len(parts) > 2 else "default"  # The region, if present

            # Check if there's a corresponding entry in variables_data
            if stage_type not in variables_data or stage_name not in variables_data[stage_type]:
                missing_in_variables.add(stage_id)

    if missing_in_variables:
        log("ERROR", f"Stage consistency validation failed: Variables missing for stages: {missing_in_variables}")
        return missing_in_variables

    return None  # Return None if validation passes

def populate_pipeline_data_with_stages(pipeline_data, pipeline_yaml, variables_data, default_regions):
    # Loop through stages in pipeline_yaml
    for stage in pipeline_yaml.get('stages', []):
        # Skip commented lines and 'qa-signoff' stages
        if isinstance(stage, str) and (stage.lstrip().startswith("#")):
            continue

        # Get template, id, type, and regions (if available)
        template = stage.get('template', '')
        stage_id = stage['parameters'].get('id')
        stage_type = stage['parameters'].get('type')

        # Use regions from pipeline_yaml if available, otherwise use default_regions
        stage_regions = stage['parameters'].get('regions')

        if stage_regions is None:
            stage_regions = default_regions

        # Skip 'qa-signoff' stages
        if stage_type == "qa-signoff":
            continue

        # Determine the stage prefix based on the template
        if "build.yml" in template:
            stage_prefix = 'build_'
        elif "deploy.yml" in template:
            stage_prefix = 'deploy_'
        else:
            continue  # Skip unknown template types

        # Create stages for each specified region
        for region in stage_regions:
            regional_stage_id = f"{stage_prefix}{stage_id}_{region}"
            pipeline_data[regional_stage_id] = {
                "type": stage_type,
                "vars": variables_data.get(regional_stage_id, {})
            }

    return pipeline_data

def add_global_defaults_from_validation(pipeline_data, validation_data):
    # Extract global defaults from validation data
    global_defaults = validation_data.get('global', {})

    # Populate each stage in pipeline_data with relevant global default values
    for stage_name, stage_data in pipeline_data.items():
        stage_type = stage_data.get('type')  # Get the type of the stage

        for key, value in global_defaults.items():
            # Check if the variable is required and if the stage type matches one of the allowed stage_types
            if value.get('required', False) and stage_type in value.get('stage_types', []):
                # Add the default value to the vars of each stage
                stage_data['vars'][key] = value.get('default')

    return pipeline_data

def add_stage_defaults_from_validation(pipeline_data, validation_data):
    # Loop through each stage in pipeline_data
    for stage_name, stage_info in pipeline_data.items():
        # Extract the main part of the stage name (e.g., "build", "deploy") and the region if any
        parts = stage_name.split('_')
        stage_key = parts[0]
        stage_region = parts[-1] if len(parts) > 2 else None

        # Check if this stage key exists in validation_data
        if stage_key in validation_data:
            # Iterate through the variables in this validation section
            for var_name, var_details in validation_data[stage_key].items():
                # Check if the stage type matches any specified types in validation
                # or if no specific type is required
                valid_for_stage = 'stage_types' not in var_details or stage_info['type'] in var_details['stage_types']

                # Check for region-specific requirements
                valid_for_region = 'regions' not in var_details or (stage_region and stage_region in var_details['regions'])

                # Check for a default value and whether the type and region match
                if valid_for_stage and valid_for_region and 'default' in var_details:
                    # Populate the default value in the stage's vars
                    stage_info['vars'][var_name] = var_details['default']

    return pipeline_data

def add_global_vars_from_repo(pipeline_data, variables_data):
    # Extract global variables from variables.json
    global_vars = variables_data.get('global', {})

    # Populate each stage in pipeline_data with global variables
    for stage in pipeline_data.values():
        # Update or add global variables in each stage's vars
        stage['vars'].update(global_vars)

    return pipeline_data

def add_stage_vars_from_repo(pipeline_data, variables_data):
    # Loop through each stage in pipeline_data
    for stage_name, stage_info in pipeline_data.items():
        # Split the stage name and extract the relevant parts
        parts = stage_name.split('_')
        stage_key, stage_type = parts[0], parts[1]

        # Determine the appropriate section in variables_data based on the stage_key
        if stage_key in variables_data:
            # Check for stage_type or its default variant in variables_data
            if stage_type in variables_data[stage_key]:
                # Update or add stage-specific variables in this stage's vars
                if 'vars' not in stage_info:
                    stage_info['vars'] = {}
                stage_info['vars'].update(variables_data[stage_key][stage_type])
            elif "default" in variables_data[stage_key]:
                # Handle the default case
                if 'vars' not in stage_info:
                    stage_info['vars'] = {}
                stage_info['vars'].update(variables_data[stage_key]["default"])

    return pipeline_data


def add_stage_vars_from_repo_broke(pipeline_data, variables_data):
    # Loop through each stage in pipeline_datas
    for stage_name, stage_info in pipeline_data.items():
        # Extract the stage-specific part of the stage name
        stage_specific_key = stage_name.split('_')[1]

        # Check if this stage-specific key exists in variables_data under the corresponding stage
        stage_key = "build" if stage_specific_key == "default" else "deploy"
        if stage_key in variables_data and stage_specific_key in variables_data[stage_key]:
            # Update or add stage-specific variables in this stage's vars
            if 'vars' not in stage_info:
                stage_info['vars'] = {}
            stage_info['vars'].update(variables_data[stage_key][stage_specific_key])

    return pipeline_data

def override_region_specific_vars(pipeline_data, validation_data):
    # Loop through pipeline data and find stages that start with "deploy_"
    for stage_name, stage_info in pipeline_data.items():
        if stage_name.startswith("deploy_"):
            # Extract the region (the token after the last "_")
            region = stage_name.rsplit('_', 1)[-1]

            # Extract the stage type
            stage_type = stage_info['type']

            # Check if the region exists in the validation data
            if region in validation_data['regions']:
                region_data = validation_data['regions'][region]

                # Loop through the variables in the region
                for var_name, var_info in region_data.items():
                    # Check if the variable's stage type matches and has a default value
                    if 'stage_types' in var_info and stage_type in var_info['stage_types'] and 'default' in var_info:
                        # Add the variable and its default value to the pipeline stage
                        pipeline_data[stage_name]['vars'][var_name] = var_info['default']

    return pipeline_data


def add_secrets_to_pipeline_data(pipeline_yaml, pipeline_data, default_regions):
    for stage in pipeline_yaml.get('stages', []):
        stage_id = stage['parameters'].get('id', '')
        secrets = stage['parameters'].get('secrets', {})
        # Use overridden regions if provided, otherwise use default regions
        provided_regions = stage['parameters'].get('regions', default_regions)

        if stage_id == 'qa_signoff':
            continue

        # Identify the stages in pipeline_data that match this stage_id
        matching_stages = [key for key in pipeline_data if key.startswith(f"deploy_{stage_id}")]

        for secret_key, secret_value in secrets.items():
            secret_assigned = False
            for region in provided_regions:
                region_suffix = f"_{region.upper()}"
                if secret_key.upper().endswith(region_suffix):
                    # Find the matching stage for this region-specific secret
                    for stage_key in matching_stages:
                        if stage_key.endswith(region.lower()):
                            pipeline_data[stage_key]['vars'][secret_key] = secret_value
                            secret_assigned = True
                            break

            # For non-region-specific secrets or if the region-specific secret has not been assigned
            if not secret_assigned:
                for stage_key in matching_stages:
                    pipeline_data[stage_key]['vars'][secret_key] = secret_value

    return pipeline_data

def validate_pipeline_data(pipeline_data, validation_data):
    errors = []

    def get_variable_type(value):
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "dict"
        elif isinstance(value, str):
            # Recognize secret placeholders for both Azure DevOps and GitHub Actions
            if value.startswith("$(") and value.endswith(")") or \
            value.startswith("${{ secrets.") and value.endswith(" }}"):
                return "secret"
            return "string"
        else:
            return "unknown"

    def check_variables(stage_type, stage_vars, required_vars, stage_name, region_specific_vars=None):
        # Extract the region from the stage name, if any
        stage_region = stage_name.rsplit('_', 1)[-1] if stage_name.count('_') > 1 else None

        for var_name, var_details in required_vars.items():
            # Skip variables not matching the stage type
            if var_details.get('stage_types') and stage_type not in var_details['stage_types']:
                continue

            # Check if the variable is required
            if var_details.get('required', False):
                if var_name not in stage_vars:
                    errors.append(f"Missing required variable '{var_name}' in '{stage_name}' stage.")
                else:
                    # Special handling for secrets
                    if var_details['type'] == 'secret':
                        if not stage_vars[var_name]:
                            errors.append(f"Missing or empty required secret '{var_name}' in '{stage_name}' stage.")
                    else:
                        # For non-secret variables, check the type
                        actual_type = get_variable_type(stage_vars.get(var_name, ""))
                        expected_type = var_details['type']
                        if actual_type != expected_type:
                            errors.append(f"Variable '{var_name}' in '{stage_name}' stage is of type '{actual_type}', expected '{expected_type}'.")

        # Check region-specific variables
        if stage_region and region_specific_vars:
            regional_vars = region_specific_vars.get(stage_region, {})
            for var_name, var_details in regional_vars.items():
                # Additional check for stage types in regional vars
                if var_details.get('stage_types') and stage_type not in var_details['stage_types']:
                    continue

                # Check if the variable is required
                if var_details.get('required', False):
                    if var_name not in stage_vars:
                        errors.append(f"Missing required variable '{var_name}' in '{stage_name}' stage (region '{stage_region}').")
                    else:
                        actual_type = get_variable_type(stage_vars.get(var_name, ""))
                        expected_type = var_details['type']
                        if actual_type != expected_type:
                            errors.append(f"Variable '{var_name}' in '{stage_name}' stage (region '{stage_region}') is of type '{actual_type}', expected '{expected_type}'.")

    # Global validation
    global_vars = validation_data.get('global', {})
    for stage_name, stage_details in pipeline_data.items():
        check_variables(stage_details['type'], stage_details['vars'], global_vars, stage_name)

    # Stage-specific validation
    for stage_category in ['build', 'deploy']:
        stage_vars = validation_data.get(stage_category, {})

        for stage_name, stage_details in pipeline_data.items():
            if stage_category in stage_name:  # Check if stage name contains the category name
                check_variables(stage_details['type'], stage_details['vars'], stage_vars, stage_name, validation_data.get('regions', {}))

    return errors

def create_validated_state(pipeline_data):
    validated_state= ""

    for stage_name, stage_data in pipeline_data.items():
        # Write the section header to the string
        validated_state += f'[{stage_name}]\n'
        if "vars" in stage_data:
            for key, value in stage_data["vars"].items():
                # Write each key-value pair to the string
                validated_state += f'{key}={value}\n'
        validated_state += '\n'  # Add a newline for separation between sections

    return validated_state

def remove_region_identifiers(validated_state):
    # Split the content into stages
    stages = re.split(r'(\[\w+\])', validated_state)

    # Process each stage
    processed_stages = []
    region = None  # Initialize region variable
    for stage in stages:
        if stage.startswith('['):  # Check if it's a stage header
            header_match = re.match(r'\[(\w+_\w+)_(\w+)\]', stage)
            if header_match:
                _, region = header_match.groups()
                region = region.upper()  # Ensure region is uppercase
            processed_stages.append(stage.strip() + '\n')  # Append the stage header with newline
        else:
            # Process the variables in the stage
            if region:
                processed_variables = []
                for line in stage.split('\n'):
                    if line.strip() and '=' in line:
                        # Split variable name and value
                        var_name, var_value = line.split('=', 1)
                        # Remove the region suffix from the variable name if present
                        if var_name.endswith(f'_{region}'):
                            var_name = var_name[:-len(region) - 1]
                        processed_variables.append(f'{var_name}={var_value}')
                processed_stage = '\n'.join(processed_variables)
                processed_stages.append(processed_stage.strip() + '\n\n')  # Append variables with newline
            else:
                # If region is not set, append the stage as is
                processed_stages.append(stage.strip() + '\n\n')  # Append non-region stage with newline

    # Combine the processed stages back into the full content
    return ''.join(processed_stages).strip()
 
def process_custom_scripts(validated_state, variables_file):
    defaults_path = os.path.normpath(os.path.join(os.getcwd(), "..", "defaults"))
    scripts_path = os.path.join(os.path.dirname(variables_file) or os.getcwd(), "scripts")
    output_path = os.path.join(output_folder, "scripts")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Updated regex pattern with non-capturing groups
    pattern = r'^(PRE_SCRIPT|POST_SCRIPT|APP_BUILD_SCRIPT|APP_DEPLOY_SCRIPT)=(.*)$'
    matches = re.findall(pattern, validated_state, re.MULTILINE)
    for full_key, value in matches:
        if value.startswith('default'):
            # Copy from default directory
            source_path = os.path.join(defaults_path, value)
            destination_path = os.path.join(output_path, value)
            copy_file(source_path, destination_path)
        else:
            # Check in custom directory
            source_path = os.path.join(scripts_path, value)
            if os.path.exists(source_path):
                destination_path = os.path.join(output_path, value)
                copy_file(source_path, destination_path)
            else:
                print(f"Error: {value} not found in {scripts_path}")

def process_helm_charts(pipeline_data,variables_file):
    output_path = os.path.join(output_folder, state_file, "charts")
    charts_path = os.path.join(os.path.dirname(variables_file) or os.getcwd(), "charts")

    # Read contents of helm chart
    with open(charts_path, 'r') as file:
        chart = file.read()

    # Substitute variable references with pipeline data values
    for key, value in pipeline_data.items():
        chart = chart.replace("${" + key + "}", str(value))

    # output helm chart
    with open(output_path, 'w') as file:
        file.write(chart)

def create_state_file(validated_state):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_path = os.path.join(output_folder, state_file)
    with open(output_path, 'w') as file:
        file.write(validated_state)

    return validated_state

def update_file_extensions(pipeline_data,validation_data):
    # Extract the supported script types and their extensions from the new location
    supported_scripts = validation_data.get('supported', {}).get('scripts', {})

    # Process each stage in the pipeline data
    for stage, stage_data in pipeline_data.items():
        stage_type = stage_data.get("type")
        stage_vars = stage_data.get("vars", {})

        # Check if the stage type is supported
        if stage_type not in supported_scripts:
            continue

        # Get the file extension for the current script type
        file_extension = supported_scripts[stage_type]

        # Update file extensions for relevant keys
        for key in ['PRE_SCRIPT', 'POST_SCRIPT', 'APP_BUILD_SCRIPT', 'APP_DEPLOY_SCRIPT']:
            if key in stage_vars:
                filename = stage_vars[key]
                new_filename = f"{filename.split('.')[0]}.{file_extension}"
                stage_vars[key] = new_filename
                print(f"Updated {key} in stage '{stage}' to: {new_filename}")

    return pipeline_data    

def copy_file(source, destination):
    # Check if the destination file already exists
    if os.path.exists(destination):
        return
    try:
        shutil.copy(source, destination)
        print(f"Copied {source} to {destination}")
    except FileNotFoundError:
        print(f"Error: {source} not found")

def log(level, message):
    print(f"[{level}] {message}")
    
    if level == "ERROR":
        exit(1)

def main(variables_file, deploy_yaml):

    # 1. Find pipeline yaml with reference to variables file
    pipeline_yaml = find_yaml_with_variables(variables_file)

    # Get validation data
    validation_data=get_validation_data()

    # Get repo variables
    variables_data=get_variables_data(variables_file)

    default_regions=get_default_regions(deploy_yaml)

    # Create object to hold our pipeline data
    pipeline_data={}

    # Populate object with stages and their types
    pipeline_data=populate_pipeline_data_with_stages(pipeline_data, pipeline_yaml, variables_data, default_regions)

    # Verify pipeline yaml and variables file match up
    try:
        validate_stage_consistency(pipeline_data, variables_data)
        log("INFO","Stage consistency validated successfully.")
    except ValueError as e:
        log("ERROR",f"Stage consistency validation failed: {str(e)}")

    # Populate pipeline data with global defaults from validation data
    pipeline_data=add_global_defaults_from_validation(pipeline_data, validation_data)

    # Populate pipeline data with stage-specific defaults from validation data
    pipeline_data=add_stage_defaults_from_validation(pipeline_data, validation_data)

    # Populate pipeline data with global vars from repo variables
    pipeline_data=add_global_vars_from_repo(pipeline_data, variables_data)

    # Populate pipeline data with stage-specific vars from repo variables
    pipeline_data=add_stage_vars_from_repo(pipeline_data, variables_data)

    # Populate pipeline data with region-specific vars from repo variables
    pipeline_data=override_region_specific_vars(pipeline_data, validation_data)

    # Populate pipeline data with secrets from repo
    pipeline_data=add_secrets_to_pipeline_data(pipeline_yaml, pipeline_data, default_regions)

    # Print out the data being validated
    pipeline_data=update_file_extensions(pipeline_data,validation_data)
    pretty_pipeline_data = json.dumps(pipeline_data, indent=4)
    log("INFO",f"Validating variables and secrets:\n{pretty_pipeline_data}")

    # Validate pipeline data
    validation_errors = validate_pipeline_data(pipeline_data, validation_data)
    if validation_errors:
        log("INFO","Validation failed with the following errors:")
        for error in validation_errors:
            log("INFO",error)
        exit(1)
    else:
        log("INFO","Variables and secrets passed successfully.")

    # Create validated state in ini format
    validated_state=create_validated_state(pipeline_data)

    # Remove region identifiers from state
    validated_state=remove_region_identifiers(validated_state)

    # Process custom scripts
    process_custom_scripts(validated_state, variables_file)
 
    # Create state file
    validated_state=create_state_file(validated_state)    

    # Process helm charts
    #helm_charts=process_helm_charts()
        
    print("\nValidated state:")
    print("---------------------------------------------------------------------------------------------------------")
    print(validated_state)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('variables_file', type=str, help='Path to the variables JSON file')
    parser.add_argument('deploy_yaml', type=str, help='Path to the deploy.yml file')

    args = parser.parse_args()
    main(args.variables_file, args.deploy_yaml)