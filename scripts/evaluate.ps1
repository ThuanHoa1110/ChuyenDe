# PowerShell script to run evaluation
param(
    [string]$Config = "configs/split.yaml",
    [string]$Checkpoint = ""
)

$venvPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { $venvPython = "python" }

Write-Host "=== Starting Evaluation Pipeline ===" -ForegroundColor Cyan
if ($Checkpoint -ne "") {
    & $venvPython -m src.weather.evaluate --config $Config --checkpoint $Checkpoint
} else {
    & $venvPython -m src.weather.evaluate --config $Config
}

