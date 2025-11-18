# Football Prediction Web App – Documentation (EN)

## Overview
This project is a Streamlit web application that predicts football match results using XGBoost models and explains predictions with SHAP values. Data is fetched from https://www.football-data.co.uk, processed locally, and stored in simple files instead of Azure services.

## Project Structure
- Root: `app.py` (Streamlit UI), `run_pipelines.py` (data + prediction pipeline).
- Core code: `src/` with packages:
  - `preprocess/` – feature engineering and league table logic.
  - `modelling/` – model training and hyperparameter search.
  - `pipelines/` – end-to-end refresh pipeline.
  - `storage/` – local storage abstraction.
  - `frontend/` – dashboard, metrics, and match reports.
  - `utils/` – configuration and shared helpers.
- Local data: `data/` (created at runtime) holds results, fixtures, processed data, models, and predictions.

## Setup & Installation
1. Create a virtual environment:
   - Windows: `python -m venv .venv` and `.\.venv\Scripts\activate`
2. Install dependencies:
   - `pip install -r requirements.txt`

## Running Pipelines and App
1. Generate or refresh local data, train a model, and create predictions:
   - `python run_pipelines.py`
2. Start the web app:
   - `streamlit run app.py`
3. Open the URL printed by Streamlit (typically `http://localhost:8501`) to interact with the dashboard.

## Storage and Data Flow
1. `run_pipelines.py` downloads raw results/fixtures from Football-Data, preprocesses them, trains/loads a model, and saves predictions into the `data/` directory.
2. The Streamlit app reads predictions from `data/` via `src/frontend/data.py`.
3. No Azure configuration is required for local usage; all files remain on your machine.
