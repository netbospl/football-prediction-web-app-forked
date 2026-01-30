# Configuration Guide

This document describes all configuration options for the Football Prediction Web App.

## Environment Variables

All configuration is done via environment variables. Create a `.env` file in the project root or set them in your shell.

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `STORAGE_BACKEND` | `local` | Storage backend: `local` or `azure` |
| `DATA_DIR` | `data` | Local directory for data files |
| `DB_PATH` | `data/app.db` | SQLite database file path |

### Azure Settings (Optional)

Only required when `STORAGE_BACKEND=azure`:

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_CONNECTION_STRING` | (empty) | Azure Blob Storage connection string |
| `AZURE_CONTAINER_NAME` | (empty) | Azure container name |

## Storage Backends

### Local Backend (Default)

Uses the local filesystem. No external credentials needed.

```bash
# .env
STORAGE_BACKEND=local
DATA_DIR=data
DB_PATH=data/app.db
```

Data structure:
```
data/
├── fixtures/
│   └── fixtures.csv
├── results/
│   └── {season}/{league}.csv
├── processed/
│   ├── train.csv
│   └── valid.csv
├── predictions/
│   └── data.parquet
├── models/
│   └── model.pkl
└── app.db  # SQLite database
```

### Azure Backend

Uses Azure Blob Storage. Requires connection credentials.

```bash
# .env
STORAGE_BACKEND=azure
AZURE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_CONTAINER_NAME=football-data
```

## Database Schema

The SQLite database (`app.db`) stores:

### runs
Pipeline/app execution records.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Auto-increment primary key |
| ts | TIMESTAMP | Execution timestamp |
| backend | TEXT | Storage backend used |
| notes | TEXT | Optional notes |
| git_sha | TEXT | Git commit SHA |

### predictions
Model predictions per run.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| run_id | INTEGER | Foreign key to runs |
| match_key | TEXT | Unique match identifier |
| f_div | TEXT | Division/league code |
| f_date | TEXT | Match date |
| f_time | TEXT | Kick-off time |
| home_team | TEXT | Home team name |
| away_team | TEXT | Away team name |
| pred_result | TEXT | Predicted result (H/D/A) |
| pred_diff | REAL | Predicted goal difference |
| pred_odds | REAL | Odds for predicted result |
| shap_top_json | TEXT | Top SHAP features (JSON) |
| raw_row_json | TEXT | Full row data (JSON) |

### trades
Recommended trades per run.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| run_id | INTEGER | Foreign key to runs |
| match_key | TEXT | Match identifier |
| side | TEXT | Bet side (H/D/A) |
| odds | REAL | Betting odds |
| score | REAL | Trade score |
| edge | REAL | Model edge |
| ev | REAL | Expected value |
| stake | REAL | Recommended stake |
| rationale_json | TEXT | Trade rationale (JSON) |

### results
Final match outcomes.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| match_key | TEXT | Unique match identifier |
| final_result | TEXT | Actual result (H/D/A) |
| final_diff | REAL | Actual goal difference |
| home_goals | INTEGER | Home team goals |
| away_goals | INTEGER | Away team goals |
| updated_at | TIMESTAMP | Last update time |

## Trade Recommendation Settings

These are configured in the Streamlit UI sidebar:

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Minimum odds | 1.2 | 1.1-3.0 | Exclude low odds bets |
| Maximum odds | 10.0 | 2.0-15.0 | Exclude high odds bets |
| Minimum edge | 5% | 0-20% | Model edge threshold |
| Bankroll | 100 | 10-10000 | For stake calculation |
| Top trades | 10 | 1-25 | Number of trades to show |

## League Codes

Supported leagues (from football-data.co.uk):

| Code | League | Data From |
|------|--------|-----------|
| E0 | England Premier League | 2005 |
| E1 | England Championship | 2005 |
| D1 | Germany Bundesliga | 2006 |
| I1 | Italy Serie A | 2005 |
| SP1 | Spain La Liga | 2005 |
| F1 | France Ligue 1 | 2005 |
| P1 | Portugal Primeira Liga | 2017 |
| N1 | Netherlands Eredivisie | 2017 |
| T1 | Turkey Super Lig | 2017 |
| B1 | Belgium First Division | 2017 |

## Example .env File

```bash
# Storage backend: "local" or "azure"
STORAGE_BACKEND=local

# Local data directory
DATA_DIR=data

# SQLite database path
DB_PATH=data/app.db

# Azure settings (only if STORAGE_BACKEND=azure)
# AZURE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
# AZURE_CONTAINER_NAME=football-data
```

## Loading Environment Variables

### From .env file

The app does not auto-load `.env` files. Use one of these methods:

**Option 1: python-dotenv**
```bash
pip install python-dotenv
```

Add to `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

**Option 2: Export manually**
```bash
# Linux/macOS
export STORAGE_BACKEND=local
export DATA_DIR=data

# Windows PowerShell
$env:STORAGE_BACKEND="local"
$env:DATA_DIR="data"

# Windows cmd
set STORAGE_BACKEND=local
set DATA_DIR=data
```

**Option 3: Use a wrapper script**
```bash
#!/bin/bash
# run.sh
set -a
source .env
set +a
streamlit run app.py
```

## Verifying Configuration

Check current config in the Streamlit sidebar or via Python:

```python
from src.utils.config import Config as cfg

print(f"Storage: {cfg.STORAGE_BACKEND}")
print(f"Data dir: {cfg.DATA_DIR}")
print(f"DB path: {cfg.DB_PATH}")
print(f"Using Azure: {cfg.use_azure()}")
```
