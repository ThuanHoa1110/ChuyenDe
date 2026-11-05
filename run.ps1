# Root PowerShell Runner for Hanoi Temperature Forecasting Project
param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet("setup", "test", "train", "evaluate", "serve", "inventory", "publish-kaggle")]
    [string]$Command,

    [string]$Config = "",
    [switch]$Smoke = $false,
    [switch]$Cuda = $false,
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

switch ($Command) {
    "setup" {
        & "$PSScriptRoot\scripts\setup.ps1" -Cuda:$Cuda
    }
    "test" {
        & "$PSScriptRoot\scripts\test.ps1" -SmokeOnly:$Smoke
    }
    "train" {
        if ($Config -ne "") {
            & "$PSScriptRoot\scripts\train.ps1" -Config $Config
        } else {
            & "$PSScriptRoot\scripts\train.ps1"
        }
    }
    "evaluate" {
        if ($Config -ne "") {
            & "$PSScriptRoot\scripts\evaluate.ps1" -Config $Config
        } else {
            & "$PSScriptRoot\scripts\evaluate.ps1"
        }
    }
    "serve" {
        & "$PSScriptRoot\scripts\serve.ps1"
    }
    "inventory" {
        python "$PSScriptRoot\scripts\inventory_check.py"
    }
    "publish-kaggle" {
        $venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
        if (-not (Test-Path $venvPython)) {
            $venvPython = "python"
        }
        if ($DryRun) {
            & $venvPython "$PSScriptRoot\scripts\publish_kaggle.py" --dry-run
        } else {
            & $venvPython "$PSScriptRoot\scripts\publish_kaggle.py"
        }
    }
}

