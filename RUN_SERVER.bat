@echo off
echo ========================================
echo UAE Legal Agent - Lite Server Launcher
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    echo [1/3] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Check .env file
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create .env with your ANTHROPIC_API_KEY
    pause
    exit /b 1
)

REM Install dependencies if needed
echo [2/3] Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements-production.txt
)

REM Run server
echo [3/3] Starting server...
echo.
echo ^>^> API Documentation: http://localhost:8002/docs
echo ^>^> Health Check: http://localhost:8002/health
echo.
python src/api/lite_server.py

pause