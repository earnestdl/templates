import os
import json
import argparse
import platform
import configparser

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

def process_secrets_working(stage_data, state, secrets, region):
    stage_name = next(iter(stage_data))
    # Use the provided state file path instead of a hardcoded filename
    stage_config = read_state_file(state, stage_name)

    for key, value in stage_config.items():
        # Check if the value potentially refers to a secret
        if "$(" in value:
            for secret_key, secret_value in secrets.items():
                # Check if the secret key starts with the state.ini key
                if secret_key.startswith(key):
                    # Check if the secret is region-specific
                    if secret_key.endswith("_" + region.upper()):
                        stage_data[stage_name]["secrets"][key] = secret_value
                        break
                    elif key == secret_key:  # Non-region specific secret
                        stage_data[stage_name]["secrets"][key] = secret_value
                        break

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

def write_export_script(stage_data, script_filename):
    # Detect OS
    os_type = platform.system()
    script_extension = ".ps1" if os_type == "Windows" else ".sh"
    newline_char = "\r\n" if script_extension == ".ps1" else "\n"

    # Detect CI/CD Platform
    if os.getenv("GITHUB_ACTIONS"):
        ci_cd_platform = "github"
    elif os.getenv("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI"):
        ci_cd_platform = "azdo"
    else:
        ci_cd_platform = "unknown"

    with open(script_filename + script_extension, 'w') as script_file:
        # Write variables
        for key, value in stage_data[next(iter(stage_data))]["variables"].items():
            if ci_cd_platform == "azdo":
                if script_extension == ".ps1":
                    script_file.write(f"Write-Host \"##vso[task.setvariable variable={key}]{value}\"{newline_char}")
                else:
                    script_file.write(f"echo '##vso[task.setvariable variable={key}]{value}'{newline_char}")
            elif ci_cd_platform == "github":
                script_file.write(f"echo '{key}={value}' >> $GITHUB_ENV{newline_char}")

        # Write secrets
        for key, value in stage_data[next(iter(stage_data))]["secrets"].items():
            if ci_cd_platform == "azdo":
                if script_extension == ".ps1":
                    script_file.write(f"Write-Host \"##vso[task.setvariable variable={key};issecret=true]{value}\"{newline_char}")
                else:
                    script_file.write(f"echo '##vso[task.setvariable variable={key};issecret=true]{value}'{newline_char}")
            elif ci_cd_platform == "github":
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
    regions_list = json.loads(regions) if regions else []
    secrets_dict = json.loads(secrets) if secrets else {}

    # Debugging
    print("Parsed Regions List:", regions_list)
    print("Parsed Secrets Dict:", secrets_dict)

    # Initialize stage data
    stage_data = initialize_stage_data(stage)

    # Add region to stage data
    stage_data = add_region_to_stage_data(stage_data, regions_list)

    # Process secrets
    region = stage_data[stage].get("region", None)
    stage_data = process_secrets(stage_data, state, secrets_dict, region)

    # Process Variables
    stage_data = process_variables(stage_data, state)

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
    parser.add_argument('stage', type=str, help='Stage to export')
    parser.add_argument('state', type=str, help='State file')
    parser.add_argument('secrets', type=str, help='Secrets for this environment')
    parser.add_argument('regions', nargs='?', type=str, default='[]', help='Regions for this environment')
    args = parser.parse_args()
    main(args.stage, args.state, args.secrets, args.regions)

