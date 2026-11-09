# PowerShell script to run inference API server
param(
    [string]$ListenHost = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$Reload = $false
)

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $projectRoot
$env:PYTHONPATH = "$projectRoot;$projectRoot\src"

$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { $venvPython = "python" }

Write-Host "=== Launching FastAPI Serving Engine ===" -ForegroundColor Cyan
Write-Host "Host: $ListenHost | Port: $Port"

$cmd = "& `"$venvPython`" -m uvicorn src.weather.api.app:app --host $ListenHost --port $Port"
if ($Reload) {
    $cmd += " --reload"
}

try {
    Invoke-Expression $cmd
} finally {
    Pop-Location
}
