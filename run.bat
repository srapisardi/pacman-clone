@echo off
REM Double-click this file to start the game.
REM Uses the bundled CoreyChowda.exe if present (no Python required); falls
REM back to running from source with Python otherwise.
setlocal

if exist "%~dp0dist\CoreyChowda.exe" (
    echo Starting Corey Chowda...
    "%~dp0dist\CoreyChowda.exe"
    exit /b 0
)

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
