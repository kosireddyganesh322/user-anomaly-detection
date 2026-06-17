@echo off
cd /d "%~dp0"
echo ===================================================
echo NFC Anomaly Detection — Master Project Startup
echo ===================================================

echo [INFO] Spawning Backend Service...
start "Anomaly Detection Backend" cmd /c "cd backend && start_backend.bat"

echo [INFO] Spawning Frontend Service...
start "Anomaly Detection Frontend" cmd /c "cd frontend && start_frontend.bat"

echo [SUCCESS] Both services launched successfully in new windows.
echo You can close this window now.
timeout /t 5
