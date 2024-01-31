Write-Host "##vso[task.setvariable variable=APPDYNAMICS_ENV]Development East"
Write-Host "##vso[task.setvariable variable=APP_DEPLOY_ARGS]${COMMON_ECHO} Deploying..."
Write-Host "##vso[task.setvariable variable=APP_DEPLOY_COMMAND]${COMMON_ECHO} Deploying..."
Write-Host "##vso[task.setvariable variable=APP_NAME]elvis"
Write-Host "##vso[task.setvariable variable=APP_PLATFORM]shoes"
Write-Host "##vso[task.setvariable variable=APP_RUNTIME_ARGS]running"
Write-Host "##vso[task.setvariable variable=ASPNETCORE_ENVIRONMENT]Development"
Write-Host "##vso[task.setvariable variable=CDP_BUILD_PATH]"
Write-Host "##vso[task.setvariable variable=CDP_COMMIT_SHA]"
Write-Host "##vso[task.setvariable variable=CDP_ENV_LONG]Development"
Write-Host "##vso[task.setvariable variable=CDP_ENV_SHORT]dev"
Write-Host "##vso[task.setvariable variable=CDP_PIPELINE_NAME]"
Write-Host "##vso[task.setvariable variable=CDP_PROCESS_SCRIPTS]${CDP_SCRIPTS_PATH}/process"
Write-Host "##vso[task.setvariable variable=CDP_REF]test"
Write-Host "##vso[task.setvariable variable=CDP_REGION_LONG]Default"
Write-Host "##vso[task.setvariable variable=CDP_REGION_SHORT]default"
Write-Host "##vso[task.setvariable variable=CDP_REPO_NAME]"
Write-Host "##vso[task.setvariable variable=CDP_RUN_ID]"
Write-Host "##vso[task.setvariable variable=CDP_STAGE_LONG]Deploy"
Write-Host "##vso[task.setvariable variable=CDP_STAGE_SHORT]deploy"
Write-Host "##vso[task.setvariable variable=CDP_STATE_SCRIPTS]${CDP_BUILD_PATH}/state/scripts"
Write-Host "##vso[task.setvariable variable=CDP_STEPS_SCRIPTS]${CDP_SCRIPTS_PATH}/steps"
Write-Host "##vso[task.setvariable variable=DEPLOY_REGION]this should go in the east region only in dev"
Write-Host "##vso[task.setvariable variable=DEPLOY_VAR_FROM_REPO]this should go in the dev deploy stage"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_CLUSTER]${APP_DEPLOY_ENV}-east.openshift-cluster.com"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_PREFIX]${APP_PLATFORM}-${APP_NAME}"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_PROJECT]${APP_PLATFORM}-${APP_NAME}-${APP_DEPLOY_ENV}"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_TOKEN]$(OPENSHIFT_TOKEN_DEV_EAST)"
Write-Host "##vso[task.setvariable variable=POST_SCRIPT]default.sh"
Write-Host "##vso[task.setvariable variable=POST_SCRIPT_ARGS]post-deploy"
Write-Host "##vso[task.setvariable variable=PRE_SCRIPT]default.sh"
Write-Host "##vso[task.setvariable variable=PRE_SCRIPT_ARGS]pre-deploy"
Write-Host "##vso[task.setvariable variable=PRE_SCRIPT_ARGS]pre-deploy"
Write-Host "##vso[task.setvariable variable=PRE_SCRIPT]default.sh"
Write-Host "##vso[task.setvariable variable=POST_SCRIPT_ARGS]post-deploy"
Write-Host "##vso[task.setvariable variable=POST_SCRIPT]default.sh"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_TOKEN]$(OPENSHIFT_TOKEN_DEV_EAST)"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_PROJECT]${APP_PLATFORM}-${APP_NAME}-${APP_DEPLOY_ENV}"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_PREFIX]${APP_PLATFORM}-${APP_NAME}"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_CLUSTER]${APP_DEPLOY_ENV}-east.openshift-cluster.com"
Write-Host "##vso[task.setvariable variable=DEPLOY_VAR_FROM_REPO]this should go in the dev deploy stage"
Write-Host "##vso[task.setvariable variable=DEPLOY_REGION]this should go in the east region only in dev"
Write-Host "##vso[task.setvariable variable=CDP_STEPS_SCRIPTS]${CDP_SCRIPTS_PATH}/steps"
Write-Host "##vso[task.setvariable variable=CDP_STATE_SCRIPTS]${CDP_BUILD_PATH}/state/scripts"
Write-Host "##vso[task.setvariable variable=CDP_STAGE_SHORT]deploy"
Write-Host "##vso[task.setvariable variable=CDP_STAGE_LONG]Deploy"
Write-Host "##vso[task.setvariable variable=CDP_RUN_ID]"
Write-Host "##vso[task.setvariable variable=CDP_REPO_NAME]"
Write-Host "##vso[task.setvariable variable=CDP_REGION_SHORT]default"
Write-Host "##vso[task.setvariable variable=CDP_REGION_LONG]Default"
Write-Host "##vso[task.setvariable variable=CDP_REF]test"
Write-Host "##vso[task.setvariable variable=CDP_PROCESS_SCRIPTS]${CDP_SCRIPTS_PATH}/process"
Write-Host "##vso[task.setvariable variable=CDP_PIPELINE_NAME]"
Write-Host "##vso[task.setvariable variable=CDP_ENV_SHORT]dev"
Write-Host "##vso[task.setvariable variable=CDP_ENV_LONG]Development"
Write-Host "##vso[task.setvariable variable=CDP_COMMIT_SHA]"
Write-Host "##vso[task.setvariable variable=CDP_BUILD_PATH]"
Write-Host "##vso[task.setvariable variable=ASPNETCORE_ENVIRONMENT]Development"
Write-Host "##vso[task.setvariable variable=APP_RUNTIME_ARGS]running"
Write-Host "##vso[task.setvariable variable=APP_PLATFORM]shoes"
Write-Host "##vso[task.setvariable variable=APP_NAME]elvis"
Write-Host "##vso[task.setvariable variable=APP_DEPLOY_COMMAND]${COMMON_ECHO} Deploying..."
Write-Host "##vso[task.setvariable variable=APP_DEPLOY_ARGS]${COMMON_ECHO} Deploying..."
Write-Host "##vso[task.setvariable variable=APPDYNAMICS_ENV]Development East"
