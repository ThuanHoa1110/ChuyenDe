# PowerShell script to run evaluation
param(
    [string]$Config = "configs/split.yaml",
    [string]$Checkpoint = ""
)

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $projectRoot
$env:PYTHONPATH = "$projectRoot;$projectRoot\src"

$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { $venvPython = "python" }

Write-Host "=== Starting Evaluation Pipeline ===" -ForegroundColor Cyan
try {
    if ($Checkpoint -ne "") {
        & $venvPython -m src.weather.evaluate --config $Config --checkpoint $Checkpoint
    } else {
        & $venvPython -m src.weather.evaluate --config $Config
    }
} finally {
    Pop-Location
}
