# Root PowerShell Runner for Hanoi Temperature Forecasting Project
param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet("setup", "test", "train", "evaluate", "serve", "inventory")]
    [string]$Command,

    [string]$Config = "",
    [switch]$Smoke = $false,
    [switch]$Cuda = $false
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
}

