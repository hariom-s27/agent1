Repository structure
-------------------

This file documents the layout of the repository and the purpose of each top-level item. Keep this short and focused so new contributors can quickly understand what matters.

- `README.md`: Project overview and quick start.
- `LICENSE`: License file (MIT).
- `.gitignore`: Files and folders ignored by git (virtualenvs, .env, caches).
- `.gitattributes`: Git attributes for handling notebooks and line endings.
- `Dockerfile`: Optional container image to run the project and notebook.
- `.dockerignore`: Files excluded from Docker build.
- `.env.example`: Template for local environment variables (do NOT commit secrets).
- `notebooks/code.ipynb`: Primary notebook containing project code and examples. This is the source notebook to edit.
- `scripts/`: Helper scripts for local setup and development.
  - `setup-venv.ps1` — create venv, install deps, register kernel.
  - `start-notebook.ps1` — start Jupyter with the `sidekick` kernel.
  - `run-tests.ps1` — run pytest locally.
  - `ollama-test.ps1` — quick Ollama smoke test (LLM integration).
  - `clean-repo.ps1` — cleanup helper to remove generated files (added by maintainer).
- `tests/`: Pytest tests.
- `.github/`: GitHub Actions workflows, CODEOWNERS, Dependabot config.

What to keep out of the repo
- Never commit `.env` or any secrets.
- Never commit the virtual environment directories (`.venv`, `.venv_clean`). These are ignored by `.gitignore`.
- Avoid committing generated notebooks or outputs; keep `code.ipynb` as the editable source and remove `executed.ipynb` when present.

If you add new tools or folders, update this file to keep the structure discoverable.
