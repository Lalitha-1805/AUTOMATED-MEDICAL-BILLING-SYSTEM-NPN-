@echo off
REM Setup Script for Medical Billing Validation System
REM Windows Batch Script

echo =====================================================
echo Medical Billing Validation System - Setup
echo =====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)

echo.
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/5] Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully

echo.
echo [4/5] Generating synthetic dataset...
python generate_dataset.py
if errorlevel 1 (
    echo Error: Failed to generate dataset
    pause
    exit /b 1
)

echo.
echo [5/5] Training ML models...
python ml/ml_models.py
if errorlevel 1 (
    echo Error: Failed to train models
    pause
    exit /b 1
)

echo.
echo =====================================================
echo Setup Complete!
echo =====================================================
echo.
echo To start the application, run:
echo     python run.py
echo.
echo Then open your browser to:
echo     http://localhost:5000
echo.
echo Default test credentials:
echo     - Hospital Staff: staff/password
echo     - Insurance Admin: admin/password
echo.
pause
