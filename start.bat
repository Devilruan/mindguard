@echo off
setlocal enabledelayedexpansion
title MindGuard Server - One-click Start

cd /d "%~dp0"

echo ============================================================
echo   Neuro-Symbolic Mental Health Screening System  v1.1.0
echo ============================================================
echo.

rem -- Step 1: locate Python --
set "PYCMD="
where py >nul 2>nul
if %errorlevel%==0 (
    set "PYCMD=py -3"
) else (
    where python >nul 2>nul
    if !errorlevel!==0 (
        set "PYCMD=python"
    ) else (
        echo [ERROR] Python not found. Please install Python 3.11 or higher first.
        pause
        exit /b 1
    )
)
echo [1/3] Using Python: %PYCMD%
%PYCMD% --version

rem -- Step 2: check and install dependencies (first run only) --
%PYCMD% -c "import fastapi, uvicorn, sqlalchemy, pydantic, docx, werkzeug, requests" >nul 2>nul
if %errorlevel% neq 0 (
    echo [2/3] First run: installing dependencies, please wait 1-3 minutes...
    %PYCMD% -m pip install --disable-pip-version-check --quiet fastapi "uvicorn[standard]" sqlalchemy pydantic python-docx Werkzeug requests reportlab "qrcode[pil]"
    if !errorlevel! neq 0 (
        echo [ERROR] Dependency installation failed. Check your network and retry.
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed.
) else (
    echo [2/3] Dependencies ready.
)

rem -- Step 3: start server and open browser --
echo [3/3] Starting server...
start "MMHS Server" /min cmd /k "%PYCMD% main.py"
timeout /t 6 /nobreak >nul
start "" "http://localhost:8000/"
echo Server started. Open http://localhost:8000/ in browser if it did not auto-open.
echo Close the "MMHS Server" window to stop the service.
echo.
pause
endlocal
