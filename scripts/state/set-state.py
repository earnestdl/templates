import os
import re
import json
import argparse
import platform
import configparser

platform_mapping_json='../../variables/state/platform-variables.json'
common_variables_json='../../variables/state/common-variables.json'
is_windows = platform.system() == 'Windows'

def log(level, message):
    print(f"[{level}] {message}")
    if level == "ERROR":
        exit(1)

def read_state_file(state_file_path, stage):
    # Initialize configparser with case-sensitive keys
    config = configparser.ConfigParser(default_section=None)
    config.optionxform = str  # Preserve case
    config.read(state_file_path)

    if stage in config:
        # Convert the SectionProxy to a dictionary while preserving case
        return {k: v for k, v in config[stage].items()}
    else:
        log("ERROR", f"Stage {stage} not found in state file.")
        return None

def initialize_stage_data(stage):
    return {stage: {"variables": {}, "secrets": {}}}

def add_region_to_stage_data(stage_data, regions):
    # Assuming stage_data has only one key, which is the stage name
    stage = next(iter(stage_data))

    # Split stage name and check if the last part is in regions
    parts = stage.split("_")
    if len(parts) > 1 and parts[-1] in regions:
        stage_data[stage]["region"] = parts[-1]

    return stage_data

def process_secrets(stage_data, state, secrets_dict, region=None):
    stage_name = next(iter(stage_data))
    stage_config = read_state_file(state, stage_name)

    for key, value in stage_config.items():
        if "$(" in value or "${{secrets." in value:
            # Handle secrets considering the region (if provided)
            if region:
                # Regional secret processing
                secret_suffix = "_" + region.upper()
                for secret_key, secret_value in secrets_dict.items():
                    if secret_key.startswith(key) and (secret_key == key or secret_key.endswith(secret_suffix)):
                        stage_data[stage_name]["secrets"][key] = secret_value
                        break
            else:
                # Non-regional secret processing
                if key in secrets_dict:
                    stage_data[stage_name]["secrets"][key] = secrets_dict[key]

    return stage_data

def add_special_variables(stage_data):
    # List of special environment variable names
    special_vars = ["CDP_BUILD_PATH", "CDP_SCRIPTS_PATH"]
    # Future special variables can be added to the above list

    # Fetch and store special environment variables
    special_env_vars = {var: os.getenv(var, '') for var in special_vars}

    # Get the stage key
    stage_key = next(iter(stage_data))

    # Merging special environment variables with existing variables
    stage_data[stage_key]['variables'] = {**special_env_vars, **stage_data[stage_key]['variables']}

    return stage_data

def add_platform_variables(stage, stage_data, platform_mapping):
    platform = detect_platform()
    if not platform:
        raise ValueError("Unable to detect the CI/CD platform.")
    
    for common_name, mappings in platform_mapping.items():
        platform_specific_var = mappings.get(platform)
        if platform_specific_var:
            # Fetch the platform-specific variable value from the environment
            value = os.getenv(platform_specific_var, '')
            # Update the config object
            stage_data[stage]['variables'][common_name] = value

    return stage_data

def add_common_variables(env, stage_data, common_variables):
    # Parsing the stage name from the stage_data key
    stage_key = next(iter(stage_data))
    stage_name = stage_key.split('_')[0]  # Gets the first token before "_"

    # Initialize a new dictionary to hold the combined variables
    combined_variables = {}

    # Add global variables
    combined_variables.update(common_variables['global'])

    # Add environment-specific variables
    if env in common_variables['environments']:
        combined_variables.update(common_variables['environments'][env])

    # Add stage-specific variables
    if stage_name in common_variables['stages']:
        combined_variables.update(common_variables['stages'][stage_name])

    # Add region-specific variables
    region = stage_data[stage_key].get('region', 'default')
    if region in common_variables['regions']:
        combined_variables.update(common_variables['regions'][region])

    # Resolve references in combined_variables
    for key, value in combined_variables.items():
        combined_variables[key] = resolve_reference(value, stage_data[stage_key]['variables'])
 
    # Merge with existing variables in stage_data
    stage_variables = stage_data[stage_key].get('variables', {})
    stage_variables.update(combined_variables)

    # Update the stage_data with the combined variables
    #stage_data[stage_key]['variables'] = stage_variables

    return stage_data

def add_state_variables(stage_data, state):
    stage_name = next(iter(stage_data))
    stage_config = read_state_file(state, stage_name)

    for key, value in stage_config.items():
        # Check if it looks like a GitHub or AzDO secret
        if "$(" in value or "${{secrets." in value:
            # If already processed as a secret, skip it
            if key in stage_data[stage_name]["secrets"]:
                continue
        
        # Process it as a variable
        stage_data[stage_name]["variables"][key] = value

    # Attempt to resolve any references within these new variables
    #stage_data = resolve_variable_references(stage_data)

    # Resolve references in stage_config
    for key, value in stage_config.items():
        stage_data[stage_name]['variables'][key] = resolve_reference(value, stage_data[stage_name]['variables'])

    return stage_data

def resolve_reference(value, existing_variables):
    if isinstance(value, str) and '${' in value:
        # Replace references with actual values
        for var_key, var_value in existing_variables.items():
            value = value.replace('${' + var_key + '}', var_value)
    return value

def resolve_variable_references(stage_data):
    variables = stage_data.get("variables", {})
    resolved = {}
    unresolved = variables.copy()

    made_progress = True
    while unresolved and made_progress:
        made_progress = False
        keys_for_removal = []
        for key, value in unresolved.items():
            try:
                formatted_value = value.format(**resolved, **variables, **os.environ)
                resolved[key] = formatted_value
                keys_for_removal.append(key)
                made_progress = True
            except KeyError as e:
                continue  # Reference not yet resolved

        for key in keys_for_removal:
            del unresolved[key]

        if not made_progress:
            print(f"Warning: Could not resolve all variable references. Some variables may be left unresolved.")

    # Add unresolved variables as-is
    resolved.update(unresolved)

    stage_data["variables"] = resolved
    return stage_data

def reorder_referenced_variables(stage_data):
    # Regular expression to match variables in the format ${...}
    variable_pattern = re.compile(r'\${[^{}]+}')

    # Get the first key in the stage_data object to use as the stage name
    stage_name = next(iter(stage_data))

    # Dictionary to temporarily store referenced variables
    referenced_variables = {}

    # Identifying and temporarily storing referenced variables
    for key, value in list(stage_data[stage_name]['variables'].items()):
        if variable_pattern.search(value):
            referenced_variables[key] = stage_data[stage_name]['variables'].pop(key)

    # Adding the referenced variables back at the bottom of the dictionary
    stage_data[stage_name]['variables'].update(referenced_variables)

    return stage_data

def write_export_script(stage_data, script_filename):
    os_type = platform.system()
    githost = detect_platform()  # Assuming this function is defined elsewhere
    script_extension = ".ps1" if os_type == "Windows" else ".sh"
    newline_char = "\r\n" if script_extension == ".ps1" else "\n"

    stage_key = next(iter(stage_data))
    variables = stage_data[stage_key]["variables"]
    secrets = stage_data[stage_key]["secrets"]

    with open(script_filename + script_extension, 'w') as script_file:
        # Write variables
        for key, value in variables.items():
            write_variable_or_secret(script_file, key, value, githost, os_type, newline_char, is_secret=False)

        # Write secrets
        for key, value in secrets.items():
            write_variable_or_secret(script_file, key, value, githost, os_type, newline_char, is_secret=True)

def write_variable_or_secret(file, key, value, githost, os_type, newline_char, is_secret):
    if githost == "azdo":
        secret_flag = ";issecret=true" if is_secret else ""
        cmd_prefix = "Write-Host" if os_type == "Windows" else "echo"
        file.write(f"{cmd_prefix} \"##vso[task.setvariable variable={key}{secret_flag}]{value}\"{newline_char}")
        # Additionally, export as an environment variable
        export_command = f"Set-Variable -Name {key} -Value '{value}'" if os_type == "Windows" else f"export {key}='{value}'"
        file.write(f"{export_command}{newline_char}")
    elif githost == "github":
        file.write(f"echo '{key}={value}' >> $GITHUB_ENV{newline_char}")
        # For GitHub Actions, the above line is sufficient to set environment variables

def print_stage_data(stage_data):
    stage_name = next(iter(stage_data))

    # Print variables
    print(f"\nProcessed variables for {stage_name}:")
    print("-" * 50)
    for key, value in stage_data[stage_name]["variables"].items():
        print(f"{key}={value}")
    print("-" * 50 + "\n")

    # Print secrets
    print(f"Processed secrets for {stage_name}:")
    print("-" * 50)
    for key, value in stage_data[stage_name]["secrets"].items():
        print(f"{key}={value}")
    print("-" * 50)

def load_platform_mapping(platform_mapping_json):
    with open(platform_mapping_json, 'r') as file:
        return json.load(file)

def load_common_variables(common_variables_json):
    with open(common_variables_json, 'r') as file:
        return json.load(file)

def detect_platform():
    # Simple detection based on environment variables
    if os.getenv('GITHUB_WORKFLOW'):
        return 'github'
    elif os.getenv('SYSTEM_TEAMFOUNDATIONCOLLECTIONURI'):
        return 'azdo'
    else:
        return None

def parse_string_to_json(json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        log("ERROR", "Invalid JSON format.")
        return None

def main(env, stage, state, secrets, regions):
    state_data = read_state_file(state, stage)
    if not state_data:
        return

    # Correctly parse regions and secrets
    try:
        secrets_dict = json.loads(secrets) if secrets else {}
    except json.JSONDecodeError as e:
        print(f"Error parsing secrets: {secrets}")
        raise e

    try:
        regions_list = json.loads(regions) if regions else []
    except json.JSONDecodeError as e:
        print(f"Error parsing regions: {regions}")
        raise e
    
    platform_mapping=load_platform_mapping(platform_mapping_json)
    common_variables=load_common_variables(common_variables_json)

    # Initialize stage data
    stage_data = initialize_stage_data(stage)

    # Add region to stage data
    stage_data = add_region_to_stage_data(stage_data, regions_list)

    # Process secrets
    region = stage_data[stage].get("region", None)
    stage_data = process_secrets(stage_data, state, secrets_dict, region)

    # Map platform variables
    stage_data = add_special_variables(stage_data)

    # Map platform variables
    stage_data = add_platform_variables(stage, stage_data, platform_mapping)

    # Adds common CDP variables
    stage_data = add_common_variables(env, stage_data, common_variables)

    # Process variables
    stage_data = add_state_variables(stage_data, state)

    reorder_referenced_variables(stage_data)

    pretty_stage_data = json.dumps(stage_data, indent=4)
    log("INFO", f"Stage data:\n{pretty_stage_data}")

    # Write export scripts
    write_export_script(stage_data,stage)

    # Write output for logging
    print_stage_data(stage_data)

    # TODO: Process Scripts

    # TODO: Process Helm Charts

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process arguments')
    parser.add_argument('env', type=str, help='Deployment environment')
    parser.add_argument('stage', type=str, help='Stage to export')
    parser.add_argument('state', type=str, help='State file')
    parser.add_argument('secrets', type=str, help='Secrets for this environment')
    parser.add_argument('regions', type=str, help='Regions for this environment')
    args = parser.parse_args()
    main(args.env,args.stage, args.state, args.secrets, args.regions)
