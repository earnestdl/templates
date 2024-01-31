Write-Host "##vso[task.setvariable variable=PRE_SCRIPT]default.sh"
Write-Host "##vso[task.setvariable variable=POST_SCRIPT]default.sh"
Write-Host "##vso[task.setvariable variable=PRE_SCRIPT_ARGS]pre-deploy"
Write-Host "##vso[task.setvariable variable=POST_SCRIPT_ARGS]post-deploy"
Write-Host "##vso[task.setvariable variable=APP_RUNTIME_ARGS]running"
Write-Host "##vso[task.setvariable variable=APP_DEPLOY_ARGS]deploy"
Write-Host "##vso[task.setvariable variable=APP_DEPLOY_COMMAND]default.sh"
Write-Host "##vso[task.setvariable variable=CDP_REPO_NAME]"
Write-Host "##vso[task.setvariable variable=CDP_BUILD_PATH]"
Write-Host "##vso[task.setvariable variable=CDP_RUN_ID]"
Write-Host "##vso[task.setvariable variable=CDP_COMMIT_SHA]"
Write-Host "##vso[task.setvariable variable=CDP_REF]test"
Write-Host "##vso[task.setvariable variable=CDP_PIPELINE_NAME]"
Write-Host "##vso[task.setvariable variable=CDP_ENV_SHORT]Development"
Write-Host "##vso[task.setvariable variable=CDP_SCRIPTS_PATH]${CDP_TEMPLATES_PATH}/scripts"
Write-Host "##vso[task.setvariable variable=CDP_PROCESS_SCRIPTS]${CDP_SCRIPTS_PATH}/process"
Write-Host "##vso[task.setvariable variable=CDP_STEPS_SCRIPTS]${CDP_SCRIPTS_PATH}/steps"
Write-Host "##vso[task.setvariable variable=CDP_STAGE_SHORT]deploy"
Write-Host "##vso[task.setvariable variable=CDP_STAGE_LONG]Deploy"
Write-Host "##vso[task.setvariable variable=CDP_TEMPLATES_PATH]${CDP_BUILD_PATH}"
Write-Host "##vso[task.setvariable variable=CDP_REGION_SHORT]default"
Write-Host "##vso[task.setvariable variable=CDP_REGIONS_LONG]Default"
