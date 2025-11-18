# Repository Guidelines

## Project Structure & Module Organization
Source files live in `src/`: `frontend/` supplies Streamlit data helpers used by `app.py`, `pipelines/` houses Azure refresh logic invoked by `run_pipelines.py`, and `preprocess/`, `modelling/`, `explain/`, `storage/`, plus `utils/` cover feature engineering, experiments, SHAP explanations, blob IO, and shared config. Notebook research stays in `train.ipynb`, while deployment automation sits under `.github/workflows`. Keep large parquet outputs in Azure Blob via the adapters instead of committing them.

## Build, Test, and Development Commands
- `python -m venv .venv && .venv\Scripts\activate`: create an isolated environment before installing anything.
- `pip install -r requirements.txt`: pull Streamlit, pandas, xgboost, SHAP, and Azure SDK dependencies.
- `streamlit run app.py`: launch the dashboard locally (it reads from the Azure bucket referenced by your `AZURE_*` vars).
- `python run_pipelines.py`: refresh fixtures/results and regenerate the `valid` prediction partition; uncomment extra blocks when reseeding train/test partitions.
- `jupyter notebook train.ipynb`: iterate on modelling or hyperopt experiments.

## Coding Style & Naming Conventions
Stick to PEP 8 with 4-space indents, snake_case modules/functions, and UpperCamelCase classes. Data columns should follow the existing `F_*` and `ODDS_*` prefixes (see `src/utils/config.py`). Keep Azure access wrappers inside `src/storage` and document complex transforms with concise docstrings or comments.

## Testing Guidelines
There is no packaged pytest suite yet, so rely on targeted validation: run `python run_pipelines.py` after touching pipelines or storage helpers, then smoke-test `streamlit run app.py` to confirm KPIs render and SHAP tables populate. For modelling tweaks, re-run `train.ipynb` cells and log metric deltas beside the saved model in Azure. When adding automated tests, mirror the module tree under `tests/` and name files `test_<feature>.py` to prepare for pytest.

## Commit & Pull Request Guidelines
Recent history shows short imperative subjects (e.g., `Update README.md`, `Remove notes`); follow that format and keep messages under ~72 characters. PRs should describe scope, list any scripts or notebooks to re-run, link issues, and include updated Streamlit screenshots whenever UI output changes. Avoid committing generated blobs unless reviewers explicitly request them.

## Security & Configuration
Secrets (`AZURE_CONNECTION_STRING`, `AZURE_CONTAINER_NAME`) are read during module import, so load them via environment variables or an ignored `.env` before running anything. Never paste connection strings, SAS tokens, or downloaded parquet files into commits; fetch data through the `AzureBlobTable` helpers instead.

