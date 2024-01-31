import os
import json
import argparse
import platform
import configparser

platform_mapping_json='../../variables/state/platform-mapping.json'
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

def process_variables(stage_data, state):
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

    return stage_data

def map_platform_variables(stage, stage_data, platform_mapping):
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

def write_export_script(stage_data, script_filename):
    os_type = platform.system()
    githost = detect_platform()
    script_extension = ".ps1" if os_type == "Windows" else ".sh"
    newline_char = "\r\n" if script_extension == ".ps1" else "\n"

    with open(script_filename + script_extension, 'w') as script_file:
        # Write variables
        for key, value in stage_data[next(iter(stage_data))]["variables"].items():
            if githost == "azdo":
                if script_extension == ".ps1":
                    script_file.write(f"Write-Host \"##vso[task.setvariable variable={key}]{value}\"{newline_char}")
                else:
                    script_file.write(f"echo '##vso[task.setvariable variable={key}]{value}'{newline_char}")
            elif githost == "github":
                script_file.write(f"echo '{key}={value}' >> $GITHUB_ENV{newline_char}")

        # Write secrets
        for key, value in stage_data[next(iter(stage_data))]["secrets"].items():
            if githost == "azdo":
                if script_extension == ".ps1":
                    script_file.write(f"Write-Host \"##vso[task.setvariable variable={key};issecret=true]{value}\"{newline_char}")
                else:
                    script_file.write(f"echo '##vso[task.setvariable variable={key};issecret=true]{value}'{newline_char}")
            elif githost == "github":
                script_file.write(f"echo '{key}={value}' >> $GITHUB_ENV{newline_char}")

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

def main(stage, state, secrets, regions):
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

    # Initialize stage data
    stage_data = initialize_stage_data(stage)

    # Add region to stage data
    stage_data = add_region_to_stage_data(stage_data, regions_list)

    # Process secrets
    region = stage_data[stage].get("region", None)
    stage_data = process_secrets(stage_data, state, secrets_dict, region)

    # Process variables
    stage_data = process_variables(stage_data, state)

    # Map platform variables
    stage_data = map_platform_variables(stage, stage_data, platform_mapping)

    pretty_stage_data = json.dumps(stage_data, indent=4)
    log("INFO", f"Stage data:\n{pretty_stage_data}")

    # Write export scripts
    #write_export_script(stage_data,stage)

    # Write output for logging
    #print_stage_data(stage_data)

    # TODO: Process Scripts

    # TODO: Process Helm Charts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process arguments')
    parser.add_argument('stage', type=str, help='Stage to export')
    parser.add_argument('state', type=str, help='State file')
    parser.add_argument('secrets', type=str, help='Secrets for this environment')
    parser.add_argument('regions', type=str, help='Regions for this environment')
    args = parser.parse_args()
    main(args.stage, args.state, args.secrets, args.regions)
