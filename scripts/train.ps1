# PowerShell script to execute training pipeline
param(
    [string]$Config = "configs/dinov3.yaml"
)

$venvPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { $venvPython = "python" }

Write-Host "=== Starting Training Pipeline ===" -ForegroundColor Cyan
Write-Host "Using configuration: $Config"
& $venvPython -m src.weather.train --config $Config

