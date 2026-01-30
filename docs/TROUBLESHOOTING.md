# Troubleshooting Guide

Common issues and solutions for the Football Prediction Web App.

## Installation Issues

### pip install fails with encoding error

**Symptom:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff
```

**Cause:** Original `requirements.txt` was UTF-16 encoded.

**Solution:** This is fixed in the current version. Re-pull the repository:
```bash
git pull origin master
pip install -r requirements.txt
```

### XGBoost installation fails on Windows

**Symptom:**
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Solution:** Install Visual C++ Build Tools:
```powershell
winget install Microsoft.VisualStudio.2022.BuildTools
```

Or download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### PyArrow installation fails

**Symptom:**
```
ERROR: Could not build wheels for pyarrow
```

**Solution:**
```bash
# Try installing without cache
pip install pyarrow --no-cache-dir

# Or install pre-built wheel
pip install pyarrow --only-binary=:all:
```

### SHAP installation hangs

**Symptom:** Installation seems stuck during SHAP compilation.

**Solution:** SHAP compiles numba extensions. Wait longer or:
```bash
pip install shap --no-cache-dir
```

## Runtime Issues

### "No prediction data available"

**Symptom:** App shows warning about missing data.

**Cause:** Pipeline hasn't been run yet.

**Solution:**
```bash
python run_pipelines.py
```

This fetches data from football-data.co.uk and generates predictions.

### "FileNotFoundError: data/predictions/data.parquet"

**Symptom:** App crashes looking for predictions file.

**Solution:** Run the full pipeline:
```bash
python run_pipelines.py
```

### Streamlit cache errors

**Symptom:**
```
CachedStFunctionWarning: Your script uses @st.cache
```

**Cause:** Old Streamlit version or cached data.

**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Or delete cache folder
rm -rf ~/.streamlit/cache  # Linux/macOS
rmdir /s %USERPROFILE%\.streamlit\cache  # Windows
```

### Port 8501 already in use

**Symptom:**
```
Address already in use
```

**Solution:**

**Linux/macOS:**
```bash
# Find process
lsof -i :8501

# Kill it
kill -9 <PID>

# Or use different port
streamlit run app.py --server.port 8502
```

**Windows:**
```powershell
# Find process
netstat -ano | findstr :8501

# Kill by PID
taskkill /PID <PID> /F

# Or use different port
streamlit run app.py --server.port 8502
```

### Azure connection errors

**Symptom:**
```
AzureException: The specified container does not exist
```

**Solution:**
1. Verify environment variables are set:
   ```bash
   echo $AZURE_CONNECTION_STRING
   echo $AZURE_CONTAINER_NAME
   ```
2. Check container exists in Azure portal
3. Use local mode if Azure isn't needed:
   ```bash
   export STORAGE_BACKEND=local
   ```

### Date parsing warnings

**Symptom:**
```
UserWarning: Parsing dates in DD/MM/YYYY format
```

**Cause:** pandas dateutil warning (harmless).

**Solution:** Already handled in code with `dayfirst=True`. Can be ignored.

## Data Issues

### Missing leagues in dropdown

**Symptom:** Some leagues don't appear in the UI.

**Cause:** No data for those leagues yet.

**Solution:** Run pipeline to fetch all league data:
```bash
python run_pipelines.py
```

### Predictions seem outdated

**Symptom:** Predictions are for old matches.

**Solution:** Refresh data:
```bash
python run_pipelines.py
```

For production, set up a cron job (Linux) or Task Scheduler (Windows).

### Model not updating

**Symptom:** Model seems to use old training data.

**Cause:** Model is cached in `data/models/model.pkl`.

**Solution:** Delete cached model to force retraining:
```bash
rm data/models/model.pkl  # Linux/macOS
del data\models\model.pkl  # Windows
python run_pipelines.py
```

## Database Issues

### SQLite database locked

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Cause:** Multiple processes accessing DB.

**Solution:**
1. Stop other Streamlit instances
2. Delete lock file if present:
   ```bash
   rm data/app.db-journal
   ```

### Corrupt database

**Symptom:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Solution:** Reset database:
```bash
rm data/app.db  # Linux/macOS
del data\app.db  # Windows
```

The database will be recreated on next app start.

## Trade Recommendation Issues

### No trades recommended

**Symptom:** "No trades meet the current criteria" message.

**Possible causes:**
1. No upcoming fixtures in date range
2. Minimum edge too high
3. Odds range too restrictive

**Solutions:**
- Expand date range to "All upcoming"
- Lower minimum edge slider
- Widen odds range

### SHAP features not showing

**Symptom:** Trade details don't show SHAP drivers.

**Cause:** SHAP columns not in predictions data.

**Solution:** Re-run pipeline to regenerate predictions with SHAP:
```bash
python run_pipelines.py
```

## Performance Issues

### App loads slowly

**Solution:**
1. Check data size in `data/predictions/data.parquet`
2. Filter to fewer leagues
3. Reduce number of games shown

### Memory errors

**Symptom:**
```
MemoryError or process killed
```

**Solution:**
```bash
# Increase available memory or reduce data
# Filter to specific leagues in the UI
# Or process fewer seasons in config
```

## Getting Help

If issues persist:

1. Check the console for detailed error messages
2. Verify all dependencies are installed:
   ```bash
   pip list | grep -E "streamlit|xgboost|shap|pandas"
   ```
3. Try a fresh virtual environment:
   ```bash
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
4. Check GitHub issues for similar problems
5. Create a new issue with:
   - Python version (`python --version`)
   - OS and version
   - Full error traceback
   - Steps to reproduce
