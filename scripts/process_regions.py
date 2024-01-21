import configparser
import json
import argparse

regions_json='regions.json'

# Existing function from the user's script
def create_regions_json(state_file):
    regions = {}

    # Iterate through the data to extract regions for each environment
    for key, value in state_file.items():
        if key.startswith("deploy_"):
            env, region = key.rsplit('_', 1)
            if env in regions:
                regions[env].append(region)
            else:
                regions[env] = [region]

    with open(regions_json, 'w') as file:
        json.dump(regions, file, indent=4)

# New function to read and parse the state.ini file
def read_ini_file(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return {s:dict(config.items(s)) for s in config.sections()}

# Main function to integrate the process
def main(ini_file_path):
    # Parse the ini file
    state_data = read_ini_file(ini_file_path)

    # Create the regions JSON file
    create_regions_json(state_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process state.ini file to generate regions.json')
    parser.add_argument('ini_file', help='The path to the state.ini file')
    args = parser.parse_args()

    main(args.ini_file)
