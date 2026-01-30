# Linux/macOS Setup Guide

This guide covers setting up the Football Prediction Web App on Linux and macOS.

## Prerequisites

- Python 3.8+ (3.10 or 3.11 recommended)
- Git
- pip

## Quick Start (Bash)

```bash
# 1. Clone the repository
git clone https://github.com/your-repo/football-prediction-web-app.git
cd football-prediction-web-app

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the data pipeline (first time only, fetches data)
python run_pipelines.py

# 5. Start the Streamlit app
streamlit run app.py
```

The app opens at `http://localhost:8501`

## Detailed Setup

### Step 1: Install Python

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip git
```

**macOS (with Homebrew):**
```bash
brew install python@3.11 git
```

Verify installation:
```bash
python3 --version
pip3 --version
```

### Step 2: Clone and Set Up Environment

```bash
# Clone
git clone https://github.com/your-repo/football-prediction-web-app.git
cd football-prediction-web-app

# Create isolated environment
python3 -m venv venv

# Activate
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note for ARM-based systems (Apple Silicon, Raspberry Pi):**
```bash
# You may need to install from source for some packages
pip install --no-binary :all: xgboost
```

### Step 4: Initialize Data

First-time setup requires running the pipeline:

```bash
python run_pipelines.py
```

This downloads fixtures and results, processes features, and generates predictions.

### Step 5: Run the App

```bash
streamlit run app.py
```

Access at `http://localhost:8501`

## Configuration (Optional)

```bash
# Copy example config
cp .env.example .env

# Edit with your preferred editor
nano .env
# or
vim .env
```

See [CONFIGURATION.md](CONFIGURATION.md) for all options.

## Running in Background

### Using nohup
```bash
nohup streamlit run app.py &
```

### Using screen
```bash
screen -S football-app
streamlit run app.py
# Detach with Ctrl+A, then D
# Reattach with: screen -r football-app
```

### Using systemd (Production)

Create `/etc/systemd/system/football-prediction.service`:
```ini
[Unit]
Description=Football Prediction Web App
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/football-prediction-web-app
ExecStart=/path/to/venv/bin/streamlit run app.py --server.port 8501
Restart=always
Environment="STORAGE_BACKEND=local"

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable football-prediction
sudo systemctl start football-prediction
```

## Scheduled Data Refresh (Cron)

Add to crontab (`crontab -e`):
```cron
# Refresh data every Wednesday and Saturday at midnight
0 0 * * 3,6 /path/to/venv/bin/python /path/to/football-prediction-web-app/run_pipelines.py >> /var/log/football-prediction.log 2>&1
```

## Common Issues

### Permission denied when creating venv
```bash
python3 -m venv venv --without-pip
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
```

### Missing Python development headers
```bash
# Ubuntu/Debian
sudo apt install python3-dev

# Fedora/RHEL
sudo dnf install python3-devel

# macOS - usually not needed with Homebrew Python
```

### XGBoost fails to install
```bash
# Install build dependencies
sudo apt install build-essential cmake  # Ubuntu
sudo dnf groupinstall "Development Tools"  # Fedora
xcode-select --install  # macOS

pip install xgboost --no-cache-dir
```

### Streamlit shows "No prediction data available"
```bash
python run_pipelines.py
```

### Port 8501 already in use
```bash
# Find and kill process
lsof -i :8501
kill -9 <PID>

# Or use different port
streamlit run app.py --server.port 8502
```

## Development Workflow

```bash
# Activate environment
source venv/bin/activate

# Run tests
pytest tests/ -v

# Refresh data
python run_pipelines.py

# Start app with auto-reload
streamlit run app.py

# Deactivate when done
deactivate
```

## Database Location

SQLite database: `data/app.db`

Reset database:
```bash
rm data/app.db
```

## Docker (Alternative)

If you prefer Docker:

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t football-prediction .
docker run -p 8501:8501 -v $(pwd)/data:/app/data football-prediction
```

## Next Steps

- See [CONFIGURATION.md](CONFIGURATION.md) for environment variables
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
