# PowerShell script to run inference API server
param(
    [string]$Host = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$Reload = $false
)

$venvPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { $venvPython = "python" }

Write-Host "=== Launching FastAPI Serving Engine ===" -ForegroundColor Cyan
Write-Host "Host: $Host | Port: $Port"

$cmd = "$venvPython -m uvicorn src.weather.api.app:app --host $Host --port $Port"
if ($Reload) {
    $cmd += " --reload"
}

Invoke-Expression $cmd

