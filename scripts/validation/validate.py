import os
import json
import yaml
import argparse

state_file='state.ini'
validation_json='validation.json'

def log(level, message):
    print(f"[{level}] {message}")
    
    if level == "ERROR":
        exit(1)

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
                        return content
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
    for stage in pipeline_data:
        if stage != "global":
            if "build" in stage:  # Check for 'build' stages
                if 'build' not in variables_data or 'default' not in variables_data['build']:
                    missing_in_variables.add(stage)
            else:
                # Split the stage name to handle region-specific names
                parts = stage.split('_')
                base_stage = parts[1]  # The base stage name (e.g., 'dev', 'qa', 'prod')
                region = parts[2] if len(parts) > 2 else None  # The region, if present

                # Check for specific region stage first, then for general stage
                if ('deploy' not in variables_data or 
                    (region and f"{base_stage}_{region}" not in variables_data['deploy']) and 
                    base_stage not in variables_data['deploy']):
                    missing_in_variables.add(stage)

    if missing_in_variables:
        log("ERROR", f"Stage consistency validation failed: Variables missing for stages: {missing_in_variables}")
        return missing_in_variables

    return None  # Return None if validation passes

def populate_pipeline_data_with_stages(pipeline_data, pipeline_yaml, variables_data, validation_data, default_regions):
    # Extract stage_types for APP_DEPLOY_REGIONS from validation_data
    deploy_region_info = validation_data.get('deploy', {}).get('APP_DEPLOY_REGIONS', {})
    allowed_stage_types = deploy_region_info.get('stage_types', [])

    # Loop through stages in pipeline_yaml
    for stage in pipeline_yaml.get('stages', []):
        # Skip commented lines and 'qa-signoff' stages
        if isinstance(stage, str) and (stage.lstrip().startswith("#")):
            continue

        # Get template, id, type, and regions (if available)
        template = stage.get('template', '')
        stage_id = stage['parameters'].get('id')
        stage_type = stage['parameters'].get('type')
        stage_regions = stage['parameters'].get('regions', default_regions)

        # Skip 'qa-signoff' stages
        if stage_type == "qa-signoff":
            continue

        # Determine the stage prefix
        stage_prefix = ''
        if "build.yml" in template:
            stage_prefix = 'build_'
        elif "deploy.yml" in template:
            stage_prefix = 'deploy_'

        # Check if the stage type is allowed and regions are applicable
        if stage_type in allowed_stage_types:
            # Create region-specific stages
            for region in stage_regions:
                regional_stage_id = f"{stage_prefix}{stage_id}_{region}"
                pipeline_data[regional_stage_id] = {
                    "type": stage_type,
                    "vars": variables_data.get(regional_stage_id, {})
                }
        else:
            # Create a single stage without region specification
            single_stage_id = f"{stage_prefix}{stage_id}"
            pipeline_data[single_stage_id] = {
                "type": stage_type,
                "vars": variables_data.get(single_stage_id, {})
            }

    return pipeline_data

def add_global_defaults_from_validation(pipeline_data, validation_data):
    # Extract global defaults from validation data
    global_defaults = validation_data.get('global', {})

    # Populate each stage in pipeline_data with global default values
    for stage in pipeline_data.values():
        for key, value in global_defaults.items():
            if 'default' in value:
                # Add the default value to the vars of each stage
                stage['vars'][key] = value['default']

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

def override_region_specific_vars(pipeline_data, variables_data):
    # Iterate through each stage in pipeline_data
    for stage_name, stage_info in pipeline_data.items():
        if stage_name.startswith("deploy_"):
            # Extract the deployment stage and region
            _, deploy_stage, region = stage_name.split('_')

            # Construct the region-specific key in variables_data
            region_specific_key = f"{deploy_stage}_{region}"

            # Check if region-specific key exists in variables_data under 'deploy'
            if 'deploy' in variables_data and region_specific_key in variables_data['deploy']:
                # Update or add region-specific variables in this stage's vars
                if 'vars' not in stage_info:
                    stage_info['vars'] = {}
                stage_info['vars'].update(variables_data['deploy'][region_specific_key])

    return pipeline_data

def add_secrets_to_pipeline_data(pipeline_yaml, pipeline_data):
    for stage in pipeline_yaml.get('stages', []):
        template = stage.get('template', '')
        stage_id = stage['parameters'].get('id', '')
        stage_type = stage['parameters'].get('type', '')
        secrets = stage['parameters'].get('secrets', {})

        # Determine the stage prefix
        stage_prefix = 'build_' if "build.yml" in template else 'deploy_'

        # Determine regions involved in this stage
        regions_involved = ['east', 'west'] if any('_EAST' in key or '_WEST' in key for key in secrets.keys()) else ['none']

        for region in regions_involved:
            # Construct the key for the pipeline_data
            pipeline_key = f"{stage_prefix}{stage_id}"
            pipeline_key += f"_{region}" if region != 'none' else ""

            # Initialize stage data in pipeline_data if not present
            if pipeline_key not in pipeline_data:
                pipeline_data[pipeline_key] = {"type": stage_type, "vars": {}}

            # Add secrets to the stage
            for secret_key, secret_value in secrets.items():
                # Determine if the secret is region-specific or global
                if region == 'none' or f'_{region.upper()}' in secret_key:
                    # Extract the actual secret name and add it to pipeline_data
                    secret_name = secret_key.split('_')[0]
                    pipeline_data[pipeline_key]['vars'][secret_name] = secret_value

    return pipeline_data

def validate_pipeline_data(pipeline_data, validation_data):
    errors = []

    def get_variable_type(value):
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict) and value.get('type') == 'secret':
            return "secret"
        elif isinstance(value, dict):
            return "dict"
        else:
            return "unknown"
        
    def check_variables(stage, stage_type, stage_vars, required_vars, stage_name):
        # Extract the region from the stage name, if any
        parts = stage_name.split('_')
        stage_region = parts[-1] if len(parts) > 2 else None

        for var_name, var_details in required_vars.items():
            # Check if the variable is region-specific and if it matches the current stage's region
            required_regions = var_details.get('regions')
            if required_regions and stage_region not in required_regions:
                continue  # Skip variables not relevant for this region

            # Skip variables not matching the stage type
            if var_details.get('stage_types') and stage_type not in var_details['stage_types']:
                continue

            if var_name not in stage_vars:
                if var_details.get('required', False):
                    errors.append(f"Missing required variable '{var_name}' in '{stage_name}' stage.")
            else:
                actual_type = get_variable_type(stage_vars[var_name])
                expected_type = var_details['type']
                if actual_type != expected_type:
                    errors.append(f"Variable '{var_name}' in '{stage_name}' stage is of type '{actual_type}', expected '{expected_type}'.")

    # Global validation
    global_vars = validation_data.get('global', {})
    for stage_name, stage_details in pipeline_data.items():
        check_variables(stage_details, stage_details['type'], stage_details['vars'], global_vars, stage_name)

    # Stage-specific validation
    for stage_category in ['build', 'deploy']:
        stage_vars = validation_data.get(stage_category, {})
        for stage_name, stage_details in pipeline_data.items():
            if stage_category in stage_name:  # Check if stage name contains the category name
                check_variables(stage_details, stage_details['type'], stage_details['vars'], stage_vars, stage_name)

    return errors

def create_ini_file(pipeline_data):

    with open(state_file, 'w') as file:
        for stage_name, stage_data in pipeline_data.items():
            # Write the section header
            file.write(f'[{stage_name}]\n')
            if "vars" in stage_data:
                for key, value in stage_data["vars"].items():
                    # Write each key-value pair
                    file.write(f'{key} = {value}\n')
            file.write('\n')  # Add a newline for separation between sections

def main(variables_file, deploy_yaml):

    # 1. Find pipeline yaml with reference to variables file
    pipeline_yaml = find_yaml_with_variables(variables_file)
    if pipeline_yaml:
        log("INFO", f"Found Pipeline YAML file")
    else:
        log("ERROR", "No matching YAML file found.")

    # 2. Get validation data
    validation_data=get_validation_data()

    # 3. Get repo variables
    variables_data=get_variables_data(variables_file)

    default_regions=get_default_regions(deploy_yaml)

    # 5. Create object to hold our pipeline data
    pipeline_data={}

    # 6. Populate object with stages and their types
    pipeline_data=populate_pipeline_data_with_stages(pipeline_data, pipeline_yaml, variables_data, validation_data, default_regions)

    # 4. Verify pipeline yaml and variables file match up
    try:
        validate_stage_consistency(pipeline_data, variables_data)
        log("INFO","Stage consistency validated successfully.")
    except ValueError as e:
        log("ERROR",f"Stage consistency validation failed: {str(e)}")

    # 7. Populate pipeline data with global defaults from validation data
    pipeline_data=add_global_defaults_from_validation(pipeline_data, validation_data)

    # 8. Populate pipeline data with stage-specific defaults from validation data
    pipeline_data=add_stage_defaults_from_validation(pipeline_data, validation_data)

    # 9. Populate pipeline data with global vars from repo variables
    pipeline_data=add_global_vars_from_repo(pipeline_data, variables_data)

    # 10. Populate pipeline data with stage-specific vars from repo variables
    pipeline_data=add_stage_vars_from_repo(pipeline_data, variables_data)

    # 11. Populate pipeline data with region-specific vars from repo variables
    pipeline_data=override_region_specific_vars(pipeline_data, variables_data)

    # 12. Populate pipeline data with secrets from repo
    pipeline_data=(pipeline_yaml, pipeline_data)

    pretty_pipeline_data = json.dumps(pipeline_data, indent=4)
    log("INFO",f"Validated state:\n{pretty_pipeline_data}")

    # 13. Validate pipeline data
    validation_errors = validate_pipeline_data(pipeline_data, validation_data)
    if validation_errors:
        log("INFO","Validation failed with the following errors:")
        for error in validation_errors:
            log("INFO",error)
        exit(1)
    else:
        log("INFO","Validation passed successfully.")


    # 12. Create ini file
    create_ini_file(pipeline_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('variables_file', type=str, help='Path to the variables JSON file')
    parser.add_argument('deploy_yaml', type=str, help='Path to the deploy.yml file')

    args = parser.parse_args()
    main(args.variables_file, args.deploy_yaml)
