# Create a virtual environment and install dependencies without requiring activation
python -m venv .venv
& .\.venv\Scripts\python -m pip install --upgrade pip
& .\.venv\Scripts\python -m pip install -r requirements.txt
& .\.venv\Scripts\python -m pip install jupyter ipykernel
& .\.venv\Scripts\python -m ipykernel install --user --name sidekick --display-name "sidekick (.venv)"
Write-Output "Setup complete. To activate the venv run: .\.venv\Scripts\Activate.ps1"
