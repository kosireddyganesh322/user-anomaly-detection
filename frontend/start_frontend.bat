@echo off
cd /d "%~dp0"
echo ===================================================
echo Starting Anomaly Detection Frontend Server
echo ===================================================

if not exist node_modules (
    echo [INFO] Installing Node.js packages (npm install)...
    cmd /c npm install
)

echo [INFO] Running Vite Development Server...
cmd /c npm run dev
pause
