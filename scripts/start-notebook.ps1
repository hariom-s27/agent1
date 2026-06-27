# Activate the venv and start Jupyter Notebook in the repo root
if (Test-Path .venv) {
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Error ".venv not found — run scripts\setup-venv.ps1 first"
    exit 1
}

jupyter notebook --notebook-dir . --no-browser
