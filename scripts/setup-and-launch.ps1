$ErrorActionPreference = "Stop"

param(
    [switch]$SkipInstall
)

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDirectory
Set-Location $repoRoot

Write-Host "Repository root:" $repoRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.9 or newer must be installed and visible in PATH."
}

$venvPath = Join-Path $repoRoot ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment in $venvPath ..."
    python -m venv $venvPath
}

$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"

if (-not $SkipInstall) {
    Write-Host "Installing/Updating Python dependencies..."
    & $pipExe install -r requirements.txt
}

Write-Host "Starting Streamlit dashboard (close the browser tab or press CTRL+C to stop)..."
& $pythonExe -m streamlit run app.py
