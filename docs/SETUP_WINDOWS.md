# Windows Setup Guide

This guide covers setting up the Football Prediction Web App on Windows 10/11.

## Prerequisites

- Python 3.8+ (3.10 or 3.11 recommended)
- Git
- pip (comes with Python)

## Quick Start (PowerShell)

```powershell
# 1. Clone the repository
git clone https://github.com/your-repo/football-prediction-web-app.git
cd football-prediction-web-app

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the data pipeline (first time only, fetches data)
python run_pipelines.py

# 5. Start the Streamlit app
streamlit run app.py
```

## Quick Start (Command Prompt / cmd.exe)

```cmd
:: 1. Clone the repository
git clone https://github.com/your-repo/football-prediction-web-app.git
cd football-prediction-web-app

:: 2. Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

:: 3. Install dependencies
pip install -r requirements.txt

:: 4. Run the data pipeline (first time only)
python run_pipelines.py

:: 5. Start the Streamlit app
streamlit run app.py
```

## Detailed Setup

### Step 1: Install Python

Download Python from [python.org](https://www.python.org/downloads/windows/).

**Important:** During installation, check "Add Python to PATH".

Verify installation:
```powershell
python --version
pip --version
```

### Step 2: Clone and Set Up Environment

```powershell
# Clone
git clone https://github.com/your-repo/football-prediction-web-app.git
cd football-prediction-web-app

# Create isolated environment
python -m venv venv

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1

# Or activate (cmd.exe)
# venv\Scripts\activate.bat
```

**Note:** If you get an execution policy error in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- `streamlit` - Web UI framework
- `xgboost` - ML model
- `shap` - Model explainability
- `pandas`, `numpy`, `pyarrow` - Data handling
- `azure-storage-blob` - Azure support (optional)

### Step 4: Initialize Data

First-time setup requires running the pipeline to fetch football data:

```powershell
python run_pipelines.py
```

This will:
1. Download fixtures from football-data.co.uk
2. Download historical results
3. Process features
4. Train/load model
5. Generate predictions with SHAP values

Data is stored in the `data/` directory.

### Step 5: Run the App

```powershell
streamlit run app.py
```

The app opens at `http://localhost:8501`

## Configuration (Optional)

Create a `.env` file for custom settings:

```powershell
# Create .env file
Copy-Item .env.example .env

# Edit with notepad or your preferred editor
notepad .env
```

See [CONFIGURATION.md](CONFIGURATION.md) for all options.

## Common Issues

### pip install fails with encoding error
The original `requirements.txt` was UTF-16 encoded. This has been fixed.
If you still have issues, re-clone the repository.

### XGBoost installation fails
Install Visual C++ Build Tools:
```powershell
# Using winget
winget install Microsoft.VisualStudio.2022.BuildTools

# Or download from:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### PyArrow installation fails
```powershell
pip install pyarrow --no-cache-dir
```

### Streamlit shows "No prediction data available"
Run the pipeline first:
```powershell
python run_pipelines.py
```

### Port 8501 already in use
```powershell
# Use a different port
streamlit run app.py --server.port 8502
```

## Development Workflow

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Run tests
pytest tests/

# Refresh data (run periodically)
python run_pipelines.py

# Start app
streamlit run app.py
```

## Database Location

SQLite database is stored at:
```
data/app.db
```

To reset the database:
```powershell
Remove-Item data\app.db
```

## Next Steps

- See [CONFIGURATION.md](CONFIGURATION.md) for environment variables
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- See [SETUP_LINUX.md](SETUP_LINUX.md) for Linux/Mac setup
