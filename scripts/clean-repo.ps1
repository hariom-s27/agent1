<#
Usage: run from repo root in PowerShell

This script removes common generated files that should not be committed,
making the repository easier to read for new contributors.
#>

Write-Output "Cleaning repository (dry-run). Use -WhatIf to preview or edit script before running.";

# Remove Python cache directories
Get-ChildItem -Path . -Recurse -Directory -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -in '__pycache__', '.ipynb_checkpoints' } | ForEach-Object {
    Write-Output "Removing: $($_.FullName)";
    Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
}

# Optionally remove temporary build artifacts
Get-ChildItem -Path . -Recurse -Include '*.pyc','*.pyo','*.tmp' -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Output "Removing file: $($_.FullName)";
    Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue
}

Write-Output "Note: This script does NOT remove virtual environments or .env files by default.";
Write-Output "If you want to remove a local .venv, delete it manually (or add it to this script).";
