param (
    [string]$INI_FILE,
    [string]$STAGE
)

$OUTPUT_FILE = "variables.ps1"

function Get-Platform {
    if ($env:GITHUB_ACTIONS) {
        return "github"
    } elseif ($env:AZURE_HTTP_USER_AGENT) {
        return "azdo"
    } else {
        return "shell"
    }
}

$platform = Get-Platform
Write-Host "Processing state for $STAGE on $platform:"
Write-Host "---------------------------------------------------"

Get-Content $INI_FILE | Select-String "\[$STAGE\]" | Out-File $OUTPUT_FILE

Get-Content $OUTPUT_FILE | ForEach-Object {
    $split = $_ -split '=', 2
    $key = $split[0]
    $value = $split[1]

    if ($key -and $value) {
        Write-Host "$key=$value"

        # Check for spaces in value and encapsulate in quotes if necessary
        if ($value -match ' ') {
            $value = "`"$value`""
        }

        switch ($platform) {
            'github' {
                # Handling for GitHub Actions
                Write-Host "::set-env name=$key::$value"
            }
            'azdo' {
                # Handling for Azure DevOps
                [System.Environment]::SetEnvironmentVariable($key, $value)
                Write-Host "##vso[task.setvariable variable=$key]$value"
            }
            'shell' {
                # Default shell export
                [System.Environment]::SetEnvironmentVariable($key, $value)
            }
        }
    }
}
