# Root PowerShell Runner for Hanoi Temperature Forecasting Project
param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet("setup", "test", "train", "evaluate", "serve", "inventory", "publish-kaggle")]
    [string]$Command,

    [string]$Config = "",
    [string]$Checkpoint = "",
    [string]$ListenHost = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$Smoke = $false,
    [switch]$Cuda = $false,
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    $venvPython = "python"
}

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
        $evalArgs = @{}
        if ($Config -ne "") { $evalArgs["Config"] = $Config }
        if ($Checkpoint -ne "") { $evalArgs["Checkpoint"] = $Checkpoint }
        & "$PSScriptRoot\scripts\evaluate.ps1" @evalArgs
    }
    "serve" {
        & "$PSScriptRoot\scripts\serve.ps1" -ListenHost $ListenHost -Port $Port
    }
    "inventory" {
        & $venvPython "$PSScriptRoot\scripts\inventory_check.py"
    }
    "publish-kaggle" {
        if ($DryRun) {
            & $venvPython "$PSScriptRoot\scripts\publish_kaggle.py" --dry-run
        } else {
            & $venvPython "$PSScriptRoot\scripts\publish_kaggle.py"
        }
    }
}

