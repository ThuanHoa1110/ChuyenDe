# PowerShell script to execute training pipeline
param(
    [string]$Config = "configs/dinov3.yaml"
)

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $projectRoot
$env:PYTHONPATH = "$projectRoot;$projectRoot\src"

$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { $venvPython = "python" }

Write-Host "=== Starting Training Pipeline ===" -ForegroundColor Cyan
Write-Host "Using configuration: $Config"
try {
    & $venvPython -m src.weather.train --config $Config
} finally {
    Pop-Location
}
