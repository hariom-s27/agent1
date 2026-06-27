# agent1

[![Python CI](https://github.com/hariom-s27/agent1/actions/workflows/python-ci.yml/badge.svg)](https://github.com/hariom-s27/agent1/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This repository contains the `agent1` project. It includes Jupyter notebooks and a local Python virtual environment (ignored via .gitignore).

## Quick start

- Activate the venv:

```powershell
.venv\\Scripts\\Activate.ps1
```

- Start Jupyter Notebook:

```powershell
jupyter notebook
```

- Use the `sidekick` kernel in Jupyter/VS Code.

## Docker

Build the Docker image and run a container that serves the notebook:

```bash
docker build -t agent1:latest .
docker run --rm -p 8888:8888 -v "$(pwd):/app" agent1:latest
```

The notebook will be available at http://localhost:8888 inside your host.

## Tests

This repo includes a minimal pytest example. Run tests locally:

```powershell
pip install pytest
pytest -q
```

