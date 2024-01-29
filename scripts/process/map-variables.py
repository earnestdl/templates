import os
import argparse
import platform

def log(level, message):
    print(f"[{level}] {message}")
    
    if level == "ERROR":
        exit(1)

def main(stage, type):
    common_vars = {}
    is_windows = platform.system() == 'Windows'

    if is_windows:
        common_vars['CDP_SCRIPT_EXT'] = 'ps1'
    else:
        common_vars['CDP_SCRIPT_EXT'] = 'sh'
    
    log("INFO","Starting default platform variable translation")

    # Detect CI/CD system
    if 'GITHUB_REPOSITORY' in os.environ:
        log("INFO","Mapping variables from Github.")
        # We are in GitHub Actions
        common_vars['CDP_REPO_PLATFORM'] = 'GITHUB'
        common_vars['CDP_REPO_NAME'] = os.environ['GITHUB_REPOSITORY']
        common_vars['CDP_BUILD_PATH'] = os.environ['BUILD_SOURCESDIRECTORY']
        common_vars['CDP_RUN_ID'] = os.environ['GITHUB_RUN_ID']
        common_vars['CDP_COMMIT_SHA'] = os.environ['GITHUB_SHA']
        common_vars['CDP_REF'] = os.environ['GITHUB_REF']
        common_vars['CDP_PIPELINE_NAME'] = os.environ['GITHUB_WORKFLOW']
        
                # Generate export commands
        with open("github_env.sh" if not is_windows else "github_env.ps1", "w") as f:
            for key, value in common_vars.items():
                if key.startswith('CDP_'):
                    if is_windows:
                        f.write(f"$env:{key} = \"{value}\"\n")
                    else:
                        f.write(f"echo \"{key}={value}\" >> $GITHUB_ENV\n")

    elif 'AZURE_HTTP_USER_AGENT' in os.environ:
        log("info","Mapping variables from Azure DevOps.")
        # We are in Azure DevOps
        common_vars['CDP_REPO_PLATFORM'] = 'AZDO'
        common_vars['CDP_REPO_NAME'] = os.environ['BUILD_REPOSITORY_NAME']
        common_vars['CDP_BUILD_PATH'] = os.environ['BUILD_SOURCESDIRECTORY']
        common_vars['CDP_RUN_ID'] = os.environ['BUILD_BUILDID']
        common_vars['CDP_COMMIT_SHA'] = os.environ['BUILD_SOURCEVERSION']
        common_vars['CDP_REF'] = os.environ['BUILD_SOURCEBRANCH']
        common_vars['CDP_PIPELINE_NAME'] = os.environ['BUILD_DEFINITIONNAME']

        # Generate export commands
        with open("azure_env.sh" if not is_windows else "azure_env.ps1", "w") as f:
            for key, value in common_vars.items():
                if key.startswith('CDP_'):
                    if is_windows:
                        f.write(f"$env:{key} = \"{value}\"\n")
                    else:
                        f.write(f"echo \"##vso[task.setvariable variable={key}]{value}\"\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process arguments')
    parser.add_argument('stage', type=str, help='Stage to map')
    parser.add_argument('type', type=str, help='Stage type to map')
    args = parser.parse_args()
    main(args.stage,args.type)
