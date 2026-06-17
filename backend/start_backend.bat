@echo off
cd /d "%~dp0\.."
echo ===================================================
echo Starting Anomaly Detection Backend Server from Root
echo ===================================================

if not exist .venv (
    echo [INFO] Creating Python virtual environment .venv at root...
    python -m venv .venv
)

echo [INFO] Activating virtual environment and verifying packages...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\pip.exe install -r backend\requirements.txt

echo [INFO] Starting FastAPI App via Uvicorn...
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause
