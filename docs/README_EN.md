# Football Prediction Web App

A machine learning-powered web application for predicting football match outcomes across major European leagues. Built with Streamlit, XGBoost, and SHAP for explainable AI.

## Features

- **Match Predictions**: Predict outcomes (Home/Draw/Away) using XGBoost regression on goal difference
- **Trade Recommendations**: AI-powered betting suggestions with edge calculation and Kelly criterion stake sizing
- **Explainability**: SHAP-based explanations showing which features drive each prediction
- **Historical Tracking**: SQLite database for storing runs, predictions, trades, and results
- **Multi-League Support**: 10 European leagues with data from football-data.co.uk
- **Flexible Storage**: Local filesystem or Azure Blob Storage backends

## Quick Start

### Prerequisites

- Python 3.8+ (3.10 or 3.11 recommended)
- Git
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/your-repo/football-prediction-web-app.git
cd football-prediction-web-app

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize data (first time only)
python run_pipelines.py

# Start the app
streamlit run app.py
```

The app opens at `http://localhost:8501`

## Project Structure

```
football-prediction-web-app/
├── app.py                      # Streamlit web UI entry point
├── run_pipelines.py            # Data pipeline orchestrator
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
│
├── src/
│   ├── db/                     # SQLite database module
│   │   ├── __init__.py         # Module exports
│   │   ├── schema.py           # Table definitions
│   │   └── client.py           # CRUD operations
│   │
│   ├── explain/                # Model explainability
│   │   └── shap.py             # SHAP value calculation
│   │
│   ├── frontend/               # Streamlit UI components
│   │   ├── data.py             # Data loading/aggregation
│   │   ├── metrics.py          # Performance metrics
│   │   └── match_report.py     # Match card rendering
│   │
│   ├── modelling/              # ML experiments
│   │   └── experiment.py       # Hyperparameter tuning
│   │
│   ├── pipelines/              # Data processing
│   │   └── update.py           # Pipeline orchestration
│   │
│   ├── preprocess/             # Feature engineering
│   │   └── features.py         # SeasonProcessor class
│   │
│   ├── storage/                # Storage backends
│   │   └── tables.py           # Local/Azure/External tables
│   │
│   ├── trades/                 # Trade recommendations
│   │   ├── __init__.py         # Module exports
│   │   └── recommend.py        # Scoring and explainability
│   │
│   └── utils/                  # Utilities
│       ├── config.py           # Configuration class
│       └── functions.py        # Helper functions
│
├── data/                       # Local data storage
│   ├── fixtures/               # Current fixtures
│   ├── results/                # Historical match results
│   ├── processed/              # Processed training data
│   ├── predictions/            # Model predictions
│   ├── models/                 # Trained models
│   └── app.db                  # SQLite database
│
├── tests/                      # Test suite
│   ├── conftest.py             # Pytest fixtures
│   ├── test_imports.py         # Import verification
│   ├── test_trade_scoring.py   # Trade logic tests
│   └── test_explainability.py  # SHAP extraction tests
│
└── docs/                       # Documentation
    ├── README_EN.md            # This file (English)
    ├── README_PL.md            # Polish documentation
    ├── SETUP_WINDOWS.md        # Windows setup guide
    ├── SETUP_LINUX.md          # Linux/macOS setup guide
    ├── CONFIGURATION.md        # Configuration reference
    └── TROUBLESHOOTING.md      # Common issues
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STORAGE_BACKEND` | `local` | Storage backend: `local` or `azure` |
| `DATA_DIR` | `data` | Local data directory |
| `DB_PATH` | `data/app.db` | SQLite database path |
| `AZURE_CONNECTION_STRING` | - | Azure Blob connection (if azure backend) |
| `AZURE_CONTAINER_NAME` | - | Azure container name (if azure backend) |

### Supported Leagues

| Code | League | Data Available From |
|------|--------|---------------------|
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

## How It Works

### Data Pipeline

1. **Fetch Fixtures**: Download current fixtures from football-data.co.uk
2. **Fetch Results**: Download historical match results by season/league
3. **Feature Engineering**: Calculate team statistics, form, position
4. **Model Training**: Train XGBoost regressor on goal difference
5. **Predictions**: Generate predictions with SHAP explanations
6. **Store**: Save to local parquet files or Azure Blob Storage

### Trade Recommendation System

The trade recommendation engine evaluates upcoming fixtures:

1. **Model Confidence**: Calculated using sigmoid function on predicted goal difference
   - `confidence = 1 / (1 + exp(-|pred_diff|))`
   - 0 goal difference → 50% confidence
   - 1 goal difference → 73% confidence
   - 2 goal difference → 88% confidence

2. **Market Implied Probability**: `1 / odds`

3. **Edge**: `model_confidence - implied_probability`

4. **Expected Value (EV)**: `edge × (odds - 1)`

5. **Stake Sizing**: Quarter-Kelly criterion
   - `stake = edge / (4 × (odds - 1))`
   - Clamped to maximum 5% of bankroll

6. **Composite Score**: Combines edge, EV, and odds sweetspot bonus

### Explainability

Each prediction includes SHAP (SHapley Additive exPlanations) values:

- **Positive SHAP**: Features pushing prediction toward home win
- **Negative SHAP**: Features pushing prediction toward away win
- **Top Drivers**: Most influential features displayed in UI and stored in database

## Database Schema

### Tables

| Table | Purpose |
|-------|---------|
| `runs` | Pipeline/app execution records |
| `predictions` | Model predictions per run |
| `trades` | Recommended trades per run |
| `results` | Final match outcomes |

### Key Fields

**predictions**:
- `match_key`: Unique identifier (date_league_home_away)
- `pred_result`: H/D/A prediction
- `pred_diff`: Predicted goal difference
- `shap_top_json`: Top 5 SHAP features

**trades**:
- `side`: Bet side (H/D/A)
- `edge`: Model advantage over market
- `ev`: Expected value
- `stake`: Recommended stake amount
- `rationale_json`: Explanation with SHAP drivers

## API Reference

### Trade Module

```python
from src.trades import TradeRecommender, TradeConfig, get_recommended_trades

# Configure trade parameters
config = TradeConfig(
    min_edge=0.05,      # Minimum 5% edge required
    min_odds=1.2,       # Minimum odds
    max_odds=10.0,      # Maximum odds
    bankroll=100.0,     # Bankroll for stake calculation
    top_n=10            # Number of trades to recommend
)

# Get recommendations
trades = get_recommended_trades(predictions_df, config)

for trade in trades:
    print(f"{trade.home_team} vs {trade.away_team}")
    print(f"  Side: {trade.side} @ {trade.odds}")
    print(f"  Edge: {trade.edge*100:.1f}%")
    print(f"  Stake: {trade.stake:.2f}")
```

### Database Module

```python
from src.db import init_db, create_run, save_predictions, save_trades

# Initialize database
init_db()

# Create a run record
run_id = create_run(notes="Daily prediction run")

# Save predictions
count = save_predictions(run_id, predictions_df)

# Save trades
trade_dicts = [t.to_dict() for t in trades]
save_trades(run_id, trade_dicts)
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_trade_scoring.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Development

### Adding New Features

1. Create feature branch: `git checkout -b feature/my-feature`
2. Implement changes with tests
3. Run tests: `pytest tests/`
4. Commit with descriptive message
5. Create pull request

### Code Style

- Use type hints for function signatures
- Follow PEP 8 guidelines
- Add docstrings for public functions
- Keep functions focused and small

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.

### Quick Fixes

**No prediction data:**
```bash
python run_pipelines.py
```

**Database issues:**
```bash
rm data/app.db  # Delete and let app recreate
```

**Port in use:**
```bash
streamlit run app.py --server.port 8502
```

## License

This project is for educational purposes. Betting involves risk; use responsibly.

## Acknowledgments

- Data source: [football-data.co.uk](https://www.football-data.co.uk/)
- ML framework: XGBoost
- Explainability: SHAP
- UI framework: Streamlit
