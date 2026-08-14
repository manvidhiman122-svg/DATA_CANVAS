@echo off
REM Quick Start Script for Data Canvas on Windows

echo.
echo ========================================
echo   Data Canvas - Quick Start
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check if install was successful
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Run Streamlit app
echo.
echo ========================================
echo   Starting Data Canvas...
echo   Open browser to: http://localhost:8501
echo   Press Ctrl+C to stop
echo ========================================
echo.

streamlit run app.py

pause
