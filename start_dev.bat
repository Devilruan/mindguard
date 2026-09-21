@echo off
chcp 936 >nul
cd /d "%~dp0"

echo [DEV RUN] starting dev server from source (bundled deps, no pip install needed)
echo.
start "" http://localhost:8000/
python dev_run.py

pause
