@echo off
REM SocialTrust Web Application Launcher for Windows

echo ======================================
echo   SocialTrust Web Application
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Flask is not installed. Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Change to src directory
cd src

REM Start the web application
echo Starting SocialTrust Web Server...
echo.
echo Once started, open your browser and go to:
echo   http://localhost:5001
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
