# Football Prediction Web App �?" Technical Documentation

## 1. Overview
The Football Prediction Web App ingests football fixtures and results, engineers features, trains XGBoost models, explains predictions with SHAP, and surfaces insights via a Streamlit dashboard backed by Azure Blob Storage and CI/CD pipelines.

## 2. Repository Layout
| Path | Purpose |
| --- | --- |
| `app.py` | Streamlit UI entry point (league filters, metrics, match reports). |
| `run_pipelines.py` | Orchestrates Azure refresh jobs for fixtures/results and validation partitions. |
| `src/frontend/` | Streamlit helpers (`data.py`, `metrics.py`, `match_report.py`). |
| `src/preprocess/` | Feature engineering (e.g., `features.py`, `league_table.py`). |
| `src/modelling/` | Training routines, Hyperopt experiments, model serialization. |
| `src/explain/` | SHAP explainability helpers. |
| `src/storage/` | Azure Blob adapters (`AzureBlobTable`, parquet IO). |
| `src/utils/config.py` | Central configuration (league metadata, paths, thresholds). |
| `.github/workflows/` | GitHub Actions workflows for CI/CD. |
| `train.ipynb` | Research notebook for model exploration and Hyperopt runs. |

## 3. Environment Setup
1. **Prerequisites:** Python 3.9+, Azure subscription with Blob Storage, Git, optional Jupyter.
2. **Virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configuration:** Start from the example env file and keep secrets only in your local copy:
   ```powershell
   copy .env.example .env
   notepad .env
   ```
   Required keys (for full Azure-enabled usage):
   ```text
   AZURE_CONNECTION_STRING=...
   AZURE_CONTAINER_NAME=...
   ```
   Optional overrides (normally you can leave the defaults from code):
   ```text
   FOOTBALL_DATA_URL=https://www.football-data.co.uk
   FOOTBALL_DATA_TABLE=mmz4281
   PREDICTED_FPATH=static/predicted.txt
   PREDICTIONS_SOURCE=azure        # or "local" for offline dashboard
   PREDICTIONS_LOCAL_PATH=data/predictions_valid.parquet
   ```
4. **Data refresh:** Run `python run_pipelines.py` after changing pipelines or storage logic.
5. **Local dashboard:** `streamlit run app.py` (loads data from Azure via helpers).
6. **Notebook work:** `jupyter notebook train.ipynb` for experimentation.

### 3.0 Configuration Reference

| Key                     | Default                                 | Required (Azure mode) | Secret | Notes |
| ----------------------- | --------------------------------------- | --------------------- | ------ | ----- |
| `AZURE_CONNECTION_STRING` | _none_                                | Yes                   | Yes    | Azure Blob connection string; not needed when `PREDICTIONS_SOURCE=local`. |
| `AZURE_CONTAINER_NAME`  | _none_                                  | Yes                   | No     | Azure Blob container name; defaults to `football-data` in `.env.example`. |
| `FOOTBALL_DATA_URL`     | `https://www.football-data.co.uk`       | No                    | No     | Base URL for raw fixtures/results CSVs. |
| `FOOTBALL_DATA_TABLE`   | `mmz4281`                               | No                    | No     | Path segment for historical results on football-data.co.uk. |
| `PREDICTED_FPATH`       | `static/predicted.txt`                  | No                    | No     | Local path used by some scripts for prediction status. |
| `PREDICTIONS_SOURCE`    | `azure`                                 | No                    | No     | `azure` to read predictions from Blob, `local` to use a local Parquet file. |
| `PREDICTIONS_LOCAL_PATH`| `data/predictions_valid.parquet`        | No                    | No     | Path to local predictions Parquet when `PREDICTIONS_SOURCE=local`. |

### 3.1 Local-only usage (without Azure)
For contributors who do not have access to the Azure storage account:
- You can still set up the environment and explore the codebase and notebook locally.
- Installing dependencies and opening `train.ipynb` works entirely on your machine; you can download raw CSVs from football-data.co.uk manually if needed.
- You can run the Streamlit dashboard in an **offline** mode if you have a local Parquet file with predictions:
  - Set `PREDICTIONS_SOURCE=local` and point `PREDICTIONS_LOCAL_PATH` at your file (e.g. `data/predictions_valid.parquet`).
  - Leave `AZURE_CONNECTION_STRING` and `AZURE_CONTAINER_NAME` unset in this mode.
  - The dashboard will read predictions from the local file, but `run_pipelines.py` and any Azure uploads remain unavailable without Azure.

## 4. Data Lifecycle
1. **Acquisition:** Raw CSVs pulled from [football-data.co.uk](https://www.football-data.co.uk/).
2. **Feature engineering:** `src/preprocess/features.py` reconstructs pre-match statistics (shots, fouls, form) and uses `LeagueTable` helpers to compute rolling aggregates.
3. **Storage:** Cleaned partitions written to Azure Blob via `src/storage/tables.py`; large parquet files stay out of git.
4. **Prediction partitions:** `run_pipelines.py` materializes `valid` predictions consumed by Streamlit; training/test partitions refreshed manually when reseeding experiments.

## 5. Modelling Workflow
- **Algorithm:** XGBoost handles sparse tabular data and missing early-season stats.
- **Hyperparameter search:** `Hyperopt` jobs defined in `src/modelling/experiment.py`; results logged in `train.ipynb`.
- **Metrics:** RMSE for optimization, downstream KPIs include accuracy and ROI as rendered by the dashboard.
- **Explainability:** `src/explain/` + SHAP provide per-feature contributions for every fixture.

## 6. Streamlit Frontend
- `src/frontend/data.py` aggregates data for metrics and rolling charts.
- `src/frontend/metrics.py` formats KPI tables and dashboards.
- `src/frontend/match_report.py` renders `FixtureReport`/`ResultReport` expanders with odds, returns, and SHAP tables.
- Accessibility reminders: keep metric labels descriptive, pair charts with textual summaries, and avoid color-only encodings.

## 7. Deployment & Operations
1. **CI/CD:** GitHub Actions build and deploy to Azure App Service on pushes to `master`.
2. **App Service:** Ensure the startup command runs `streamlit run app.py`.
3. **Scheduled refresh:** VM cron entries (e.g., `0 0 * * 3,6 /usr/bin/python /home/site/wwwroot/run_pipelines.py`) keep predictions up to date; use absolute paths.
4. **Monitoring:** Streamlit logs available via App Service diagnostics; Azure Blob metrics verify data freshness.

## 8. Troubleshooting
| Symptom | Resolution |
| --- | --- |
| Streamlit shows empty tables | Verify `AZURE_*` env vars and that `valid` partition exists in Blob. |
| Pipelines fail on missing features | Rerun preprocessing notebooks and confirm schema alignment in `Config.FEATURES`. |
| SHAP tables blank | Ensure SHAP columns are present and non-zero; retrain if the schema changed. |
| Cron job not running | Confirm `crontab -l`, check executable permissions, and restart the VM if necessary. |

## 9. Future Work
- Automate model retraining with Azure ML or Synapse.
- Add pytest suites under `tests/`.
- Replace cron with Event Grid + Functions for on-demand refresh.
- Improve multi-column layouts for better keyboard navigation.
