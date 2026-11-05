# PowerShell script to run pytest tests
param(
    [string]$Target = "tests",
    [switch]$SmokeOnly = $false
)

$ErrorActionPreference = "Stop"
$venvPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    $venvPython = "python"
}

Write-Host "=== Running Pytest Test Suite ===" -ForegroundColor Cyan
if ($SmokeOnly) {
    Write-Host "Running smoke tests only..." -ForegroundColor Yellow
    & $venvPython -m pytest tests/test_smoke.py -v
} else {
    Write-Host "Running tests in $Target..." -ForegroundColor Yellow
    & $venvPython -m pytest $Target -v
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "All tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "Tests failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

