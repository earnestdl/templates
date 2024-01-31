Write-Host "##vso[task.setvariable variable=PRE_SCRIPT]default.sh"
Write-Host "##vso[task.setvariable variable=POST_SCRIPT]default.sh"
Write-Host "##vso[task.setvariable variable=PRE_SCRIPT_ARGS]pre-deploy"
Write-Host "##vso[task.setvariable variable=POST_SCRIPT_ARGS]post-deploy"
Write-Host "##vso[task.setvariable variable=APP_RUNTIME_ARGS]running"
Write-Host "##vso[task.setvariable variable=APP_DEPLOY_ARGS]deploy"
Write-Host "##vso[task.setvariable variable=APP_DEPLOY_COMMAND]default.sh"
