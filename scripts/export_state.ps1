# Usage: .\script.ps1 -IniFile "ini_file" -Stage "stage" -Platform "platform"
# Example: .\script.ps1 -IniFile ".\variables.ini" -Stage "build_default" -Platform "azdo"

param (
    [String]$IniFile,
    [String]$Stage,
    [String]$Platform
)

$iniContent = Get-Content $IniFile
$sectionFound = $false

foreach ($line in $iniContent) {
    if ($line -like "[$Stage]") {
        $sectionFound = $true
        continue
    }

    if ($sectionFound -and $line -match "^\[.*\]$") {
        break
    }

    if ($sectionFound -and $line -match "^(.*?)\s*=\s*(.*)$") {
        $name = $matches[1]
        $value = $matches[2]

        if ($Platform -eq "azdo") {
            Write-Host "##vso[task.setvariable variable=$name]$value"
        } elseif ($Platform -eq "github") {
            "$name=$value" | Out-File -Append -FilePath $env:GITHUB_ENV
        }
    }
}
