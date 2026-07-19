@echo off
title AUTOPAD Server
echo ============================================
echo    AUTOPAD Server - Auto Setup
echo ============================================
echo.

echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
echo Python found!
echo.

echo [2/3] Installing dependencies...
pip install -r requirements.txt --quiet
echo Dependencies installed!
echo.

echo [3/3] Starting AUTOPAD Server...
echo.
python gui_server.py

pause
