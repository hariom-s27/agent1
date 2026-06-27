# Activate venv and run pytest
if (Test-Path .venv) {
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Error ".venv not found — run scripts\setup-venv.ps1 first"
    exit 1
}

pip install -r requirements.txt
pytest -q
