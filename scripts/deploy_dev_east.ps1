Write-Host "##vso[task.setvariable variable=APP_REGISTRY_URL]myregistry.com"
Write-Host "##vso[task.setvariable variable=APP_RUNTIME_ARGS]-e APP_NAME=${APP_NAME} -e ASPNETCORE_ENVIRONMENT=${ASPNETCORE_ENVIRONMENT}"
Write-Host "##vso[task.setvariable variable=APP_NAME]myapp"
Write-Host "##vso[task.setvariable variable=APP_PLATFORM]edv"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_PREFIX]${APP_PLATFORM}-${APP_NAME}"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_PROJECT]${APP_PLATFORM}-${APP_NAME}-${APP_DEPLOY_ENV}"
Write-Host "##vso[task.setvariable variable=ASPNETCORE_ENVIRONMENT]Development"
Write-Host "##vso[task.setvariable variable=APP_DEPLOY_ENV]dev"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_CLUSTER]${APP_DEPLOY_ENV}-east.openshift-cluster.com"
Write-Host "##vso[task.setvariable variable=OPENSHIFT_TOKEN;issecret=true]$(OPENSHIFT_TOKEN_DEV_E1)"
Write-Host "##vso[task.setvariable variable=API_KEY;issecret=true]API_KEY=$(API_KEY_DEV)"
