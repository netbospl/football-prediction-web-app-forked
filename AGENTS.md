# Repository Guidelines

This repository contains a Streamlit-based football prediction web app backed by offline training pipelines and Azure Blob storage.

## Project Structure & Module Organization
- Application entrypoint: `app.py` (Streamlit UI) and `run_pipelines.py` (data/model refresh).
- Core Python packages live in `src/` with submodules: `preprocess/`, `modelling/`, `pipelines/`, `storage/`, `utils/`, `frontend/`, and `explain/`.
- CI/CD workflows are under `.github/workflows/`. Notebooks and experimentation live in `train.ipynb`.

## Build, Test, and Development Commands
- Create a virtualenv and install dependencies: `python -m venv .venv`, then `.\.venv\Scripts\activate`, `pip install -r requirements.txt`.
- Run the web app locally: `streamlit run app.py`.
- Run data/model pipelines manually (e.g. to refresh blobs): `python run_pipelines.py`.

## Coding Style & Naming Conventions
- Use Python 3 type hints where practical and 4-space indentation.
- Prefer descriptive snake_case for variables/functions and PascalCase for classes.
- Keep modules cohesive by domain (e.g. new preprocessing logic in `src/preprocess/`, new UI elements in `src/frontend/`).

## Testing Guidelines
- When adding features, include lightweight, focused tests (e.g. `pytest`-style) near the relevant module or in a `tests/` package if introduced.
- Favor deterministic, pure functions for core logic so they are easy to test, and avoid hitting Azure services in unit tests (mock I/O and network).

## Commit & Pull Request Guidelines
- Write clear commit messages in the style: `area: short imperative summary` (e.g. `frontend: add match report table`).
- For pull requests, include: purpose/summary, key implementation notes, any configuration changes (Azure, cron, environment variables), and screenshots for UI changes.
- Link related issues or discussion where applicable, and ensure the app starts locally (`streamlit run app.py`) before requesting review.

