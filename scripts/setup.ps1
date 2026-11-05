# PowerShell script for setting up development environment
param(
    [switch]$Cuda = $false
)

$ErrorActionPreference = "Stop"
Write-Host "=== [1/3] Checking Python Environment ===" -ForegroundColor Cyan
$pythonVersion = python --version
Write-Host "Detected Python: $pythonVersion"

$venvPath = Join-Path $PSScriptRoot "..\.venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath..." -ForegroundColor Yellow
    python -m venv $venvPath
} else {
    Write-Host "Virtual environment already exists at $venvPath" -ForegroundColor Green
}

$venvPython = Join-Path $venvPath "Scripts\python.exe"
$venvPip = Join-Path $venvPath "Scripts\pip.exe"

Write-Host "=== [2/3] Upgrading pip and installing dependencies ===" -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip

if ($Cuda) {
    Write-Host "Installing PyTorch with CUDA 12.1/12.4 support..." -ForegroundColor Yellow
    & $venvPip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
} else {
    Write-Host "Installing default PyTorch..." -ForegroundColor Yellow
    & $venvPip install torch torchvision
}

$reqFile = Join-Path $PSScriptRoot "..\requirements.txt"
Write-Host "Installing requirements from $reqFile..." -ForegroundColor Yellow
& $venvPip install -r $reqFile

Write-Host "=== [3/3] Verifying Setup ===" -ForegroundColor Cyan
& $venvPython -c "import torch; import pandas; import numpy; print(f'PyTorch: {torch.__version__} | CUDA Available: {torch.cuda.is_available()} | NumPy: {numpy.__version__}')"

Write-Host "Setup completed successfully!" -ForegroundColor Green

