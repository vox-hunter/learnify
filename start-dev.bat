@echo off
REM Learnify - Development Startup Script for Windows
REM This script starts both the FastAPI backend and Vue.js frontend

echo ========================================
echo   AI Loom Server Setup
echo ========================================
echo.

REM Check if .env exists
if not exist "api\.env" (
    echo [WARNING] api\.env not found!
    if exist "api\.env.example" (
        echo Creating from api\.env.example...
        copy "api\.env.example" "api\.env"
        echo.
        echo [ERROR] Please edit api\.env with your API keys and MongoDB URI
        echo Then run this script again.
        pause
        exit /b 1
    ) else (
        echo [ERROR] api\.env.example not found
        pause
        exit /b 1
    )
)

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1

if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [OK] Prerequisites check passed
echo.

REM Create virtual environment if needed
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

REM Install backend dependencies
echo [INFO] Installing backend dependencies...
call venv\Scripts\activate.bat
pip install -q -r api\requirements.txt

REM Install frontend dependencies if needed
if not exist "vue-frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd vue-frontend
    call npm install
    cd ..
)

echo.
echo [OK] Dependencies installed
echo.

REM Start backend in new window
echo [INFO] Starting FastAPI backend with New Relic agent...
start "Learnify Backend" cmd /k "cd api && ..\venv\Scripts\activate.bat && set NEW_RELIC_CONFIG_FILE=../newrelic.ini && ..\venv\Scripts\newrelic-admin.exe run-program python main.py"
REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo [INFO] Starting Vue.js frontend...
start "Learnify Frontend" cmd /k "cd vue-frontend && npm run dev"

echo.
echo ========================================
echo   Learnify is starting!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Check the new windows for server output
echo Close those windows to stop the servers
echo.
pause
