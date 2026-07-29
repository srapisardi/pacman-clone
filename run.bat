@echo off
REM Double-click this file to install dependencies (first run only) and start the game.
setlocal

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python was not found on your PATH. Install Python 3 from https://www.python.org/downloads/ and try again.
    pause
    exit /b 1
)

echo Installing/updating dependencies...
python -m pip install --quiet -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo Failed to install dependencies. See the error above.
    pause
    exit /b 1
)

echo Starting Corey Chowda...
python "%~dp0main.py"

pause
