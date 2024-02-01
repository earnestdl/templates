Write-Host "##vso[task.setvariable variable=ENV]dev"
Write-Host "##vso[task.setvariable variable=CDP_BUILD_PATH]"
Write-Host "##vso[task.setvariable variable=CDP_SCRIPTS_PATH]"
Write-Host "##vso[task.setvariable variable=CDP_REPO_NAME]"
Write-Host "##vso[task.setvariable variable=CDP_RUN_ID]"
Write-Host "##vso[task.setvariable variable=CDP_COMMIT_SHA]"
Write-Host "##vso[task.setvariable variable=CDP_REF]"
Write-Host "##vso[task.setvariable variable=CDP_PIPELINE_NAME]"
Write-Host "##vso[task.setvariable variable=CDP_PROCESS_SCRIPTS]/process"
Write-Host "##vso[task.setvariable variable=CDP_STEPS_SCRIPTS]/steps"
Write-Host "##vso[task.setvariable variable=CDP_STATE_SCRIPTS]/state/scripts"
Write-Host "##vso[task.setvariable variable=CDP_DEFAULT_SCRIPTS]/defaults"
Write-Host "##vso[task.setvariable variable=CDP_ENV_SHORT]dev"
Write-Host "##vso[task.setvariable variable=CDP_ENV_LONG]Development"
Write-Host "##vso[task.setvariable variable=ASPNETCORE_ENVIRONMENT]Development"
Write-Host "##vso[task.setvariable variable=CDP_STAGE_SHORT]deploy"
Write-Host "##vso[task.setvariable variable=CDP_STAGE_LONG]Deploy"
Write-Host "##vso[task.setvariable variable=CDP_REGION_SHORT]east"
Write-Host "##vso[task.setvariable variable=CDP_REGION_LONG]East"
Write-Host "##vso[task.setvariable variable=PRE_SCRIPT]/defaults/default.sh"
Write-Host "##vso[task.setvariable variable=POST_SCRIPT]/defaults/default.sh"
Write-Host "##vso[task.setvariable variable=APP_COMMAND_INT]bash -c"
Write-Host "##vso[task.setvariable variable=PRE_SCRIPT_ARGS]pre-deploy"
Write-Host "##vso[task.setvariable variable=POST_SCRIPT_ARGS]post-deploy"
Write-Host "##vso[task.setvariable variable=APP_RUNTIME_ARGS]running"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_PREFIX]shoes-elvis"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_PROJECT]shoes-elvis-dev"
Write-Host "##vso[task.setvariable variable=APP_DEPLOY_ARGS]--cluster=cluster"
Write-Host "##vso[task.setvariable variable=APP_DEPLOY_COMMAND]/process/deploy-openshift.sh"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_CLUSTER]dev-east.openshift-cluster.com"
Write-Host "##vso[task.setvariable variable=APP_NAME]elvis"
Write-Host "##vso[task.setvariable variable=APP_PLATFORM]shoes"
Write-Host "##vso[task.setvariable variable=DEPLOY_VAR_FROM_REPO]this should go in the dev deploy stage"
Write-Host "##vso[task.setvariable variable=DEPLOY_REGION]this should go in the east region only in dev"
Write-Host "##vso[task.setvariable variable=APPDYNAMICS_ENV]Development East"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_TOKEN]\$(OPENSHIFT_TOKEN_DEV_EAST)"
