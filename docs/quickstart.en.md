# Quick Start �?" Football Prediction Web App

This guide is written for non-technical teammates. Every major action is reduced to either a single command or a helper script.

## 1. Collect What You Need
1. **Ask the project owner** for permission to the GitHub repo and the Azure Blob container.
2. **Install Python 3.9+** from [python.org](https://www.python.org/downloads/). During installation, tick "Add Python to PATH".
3. **Download the project ZIP** from GitHub (green "Code" button ��' "Download ZIP"), then unzip it somewhere simple, e.g. `Documents\football-prediction-web-app-forked`.

## 2. Add Your Secrets (one-time)
1. Open **Windows Terminal ��' PowerShell**.
2. Run a single line to jump into the project folder (adjust the path if needed):
   ```
   cd "%USERPROFILE%\Documents\football-prediction-web-app-forked"
   ```
3. Create your personal settings file from the template:
   ```
   copy .env.example .env
   ```
4. Open it for editing:
   ```
   notepad .env
   ```
5. Paste the connection string you received from the owner (or update the placeholders):
   ```
   AZURE_CONNECTION_STRING=paste_value_here
   AZURE_CONTAINER_NAME=football-data
   ```
   You can also override optional settings if instructed (most users do not need this):
   ```
   FOOTBALL_DATA_URL=https://www.football-data.co.uk
   FOOTBALL_DATA_TABLE=mmz4281
   PREDICTED_FPATH=static/predicted.txt
   ```
   Save and close Notepad. You never commit this file.

## 3. Launch the Dashboard (single command)
1. In the same PowerShell window, run the helper script. It creates the virtual environment, installs packages, and opens Streamlit automatically:
   ```
   powershell -ExecutionPolicy Bypass -File ".\scripts\setup-and-launch.ps1"
   ```
2. Wait until a browser tab opens. Explore metrics, select leagues, and open match reports.
3. When finished, return to PowerShell and press `Ctrl+C` to stop Streamlit. The script exits on its own.

> **Tip:** If Windows blocks scripts, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once before the command above.

## 4. Refresh Predictions (single command, optional)
Run this only when asked to update Azure with the newest fixtures:
```
powershell -ExecutionPolicy Bypass -File ".\scripts\refresh-predictions.ps1"
```
The script ensures dependencies are ready, pulls new data, and uploads fresh metrics.

## 4a. Running without Azure (local-only)
If you do **not** have access to the Azure storage account, you still have two options:

1. **Local-only experimentation (no dashboard data)**
   - Clone the repo, create the virtual environment, and install dependencies.
   - Open and run the research notebook locally:
     - `python -m venv .venv`, activate it, `pip install -r requirements.txt`
     - `jupyter notebook train.ipynb`

2. **Offline dashboard using a local predictions file**
   - Obtain a Parquet file with predictions (for example `data/predictions_valid.parquet`) from someone who has run the pipelines.
   - In `.env`, set:
     ```text
     PREDICTIONS_SOURCE=local
     PREDICTIONS_LOCAL_PATH=data/predictions_valid.parquet
     ```
   - You can omit `AZURE_CONNECTION_STRING` and `AZURE_CONTAINER_NAME` in this mode, but:
     - The refresh script (`refresh-predictions.ps1`) and `run_pipelines.py` will **not** work without Azure.
   - Now run:
     ```powershell
     powershell -ExecutionPolicy Bypass -File ".\scripts\setup-and-launch.ps1"
     ```
     The dashboard will read predictions from the local Parquet file instead of Azure.

## 5. At-a-glance Checklist
- `copy .env.example .env` ��' `notepad .env` ��' paste secrets ��' save.
- `powershell -ExecutionPolicy Bypass -File ".\scripts\setup-and-launch.ps1"` ��' dashboard.
- `powershell -ExecutionPolicy Bypass -File ".\scripts\refresh-predictions.ps1"` ��' refresh job.

## Need Help?
- **Invalid connection string:** reopen `.env` with `notepad .env` and confirm there are no stray spaces.
- **Script blocked:** run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` inside PowerShell and retry.
- **Streamlit tab blank:** ensure the console window that launched it is still running; relaunch if it closed.
- **Refresh failed:** copy the red error text and send it to the engineering team�?"they will inspect the data pipeline.
