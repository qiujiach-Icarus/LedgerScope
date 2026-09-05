@echo off
echo ======================================================
echo   VoucherGuard AI - One-Click Setup & Launcher
echo ======================================================
echo.

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.9+ first.
    pause
    exit /b
)

:: 2. Check for Node.js
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js first.
    pause
    exit /b
)

:: 3. Create necessary directories
if not exist "data\raw" mkdir "data\raw"
if not exist "data\output" mkdir "data\output"

:: 4. Install Python Dependencies
echo [1/3] Installing Python dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b
)

:: 5. Install Frontend Dependencies
echo [2/3] Installing Frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Frontend dependencies.
    cd ..
    pause
    exit /b
)
cd ..

:: 6. Launch Services
echo [3/3] Launching VoucherGuard AI...
echo.
echo [*] Backend will run at http://localhost:8000
echo [*] Frontend will run at http://localhost:5173
echo.
echo Starting Backend...
start "VoucherGuard Backend" cmd /k "python src/app.py"

echo Starting Frontend...
cd frontend
start "VoucherGuard Frontend" cmd /k "npm run dev"

echo.
echo ======================================================
echo   Setup Complete! Your browser should open soon.
echo ======================================================
pause
