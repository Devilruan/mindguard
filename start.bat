@echo off
setlocal enabledelayedexpansion
title MindGuard Server - One-click Start
cd /d "%~dp0"
chcp 65001 >nul

echo ============================================================
echo   MindGuard 心理健康风险智能筛查系统  一键启动
echo   免配置环境：自动探测 Python / 自动安装依赖
echo ============================================================
echo.

rem ---------- 解析 PowerShell（优先使用系统全路径，避免 PATH 异常导致失败） ----------
set "PS_CMD=powershell"
if exist "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" set "PS_CMD=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

rem ============================================================
rem 读取 .env 中的 APP_HOST / APP_PORT（若存在），默认 127.0.0.1:8000
rem 默认只监听本机，避免触发 Windows 防火墙弹窗；如需局域网访问，
rem 请在 .env 中设置 APP_HOST=0.0.0.0
rem ============================================================
set "APP_HOST=127.0.0.1"
set "APP_PORT=8000"
if exist .env (
    for /f "tokens=2 delims==" %%a in ('findstr /b /i /r "APP_PORT[ =]" .env 2^>nul') do set "APP_PORT=%%a"
    for /f "tokens=2 delims==" %%a in ('findstr /b /i /r "APP_HOST[ =]" .env 2^>nul') do set "APP_HOST=%%a"
)
set "APP_PORT=!APP_PORT:"=!"
set "APP_PORT=!APP_PORT: =!"
set "APP_HOST=!APP_HOST:"=!"
set "APP_HOST=!APP_HOST: =!"

rem ============================================================
rem 0) 优先使用项目虚拟环境（.venv）—— 首次运行自动创建，之后秒开
rem ============================================================
set "VENV_PY=%~dp0.venv\Scripts\python.exe"
set "PYCMD="
set "NO_VENV="
if exist "%VENV_PY%" (
    "%VENV_PY%" -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYCMD=%VENV_PY%"
    ) else (
        echo [提示] 项目虚拟环境不可用，正在重建...
        rmdir /s /q .venv >nul 2>nul
    )
)
if defined PYCMD goto PY_READY

rem ============================================================
rem 1) 探测系统 Python（py 启动器 / PATH / 常见安装目录）
rem ============================================================
rem 1a) py 启动器
where py >nul 2>nul
if !errorlevel! equ 0 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info>=(3,10) else 1)" >nul 2>nul
    if !errorlevel! equ 0 set "PYCMD=py -3"
)
if defined PYCMD goto PY_READY

rem 1b) PATH 中的 python / python3（商店占位符会自动被版本检查淘汰）
where python >nul 2>nul
if !errorlevel! equ 0 (
    python -c "import sys; raise SystemExit(0 if sys.version_info>=(3,10) else 1)" >nul 2>nul
    if !errorlevel! equ 0 set "PYCMD=python"
)
if defined PYCMD goto PY_READY

where python3 >nul 2>nul
if !errorlevel! equ 0 (
    python3 -c "import sys; raise SystemExit(0 if sys.version_info>=(3,10) else 1)" >nul 2>nul
    if !errorlevel! equ 0 set "PYCMD=python3"
)
if defined PYCMD goto PY_READY

rem 1c) 常见安装目录（未加入 PATH 的情况也能找到）
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "C:\Python310\python.exe"
    "C:\Python311\python.exe"
    "C:\Python312\python.exe"
    "C:\Python313\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles(x86)%\Python310\python.exe"
    "%ProgramFiles(x86)%\Python311\python.exe"
    "%ProgramFiles(x86)%\Python312\python.exe"
    "%ProgramFiles(x86)%\Python313\python.exe"
    "%USERPROFILE%\anaconda3\python.exe"
    "%USERPROFILE%\miniconda3\python.exe"
    "C:\ProgramData\Anaconda3\python.exe"
    "C:\ProgramData\Miniconda3\python.exe"
) do (
    if exist %%P (
        %%P -c "import sys; raise SystemExit(0 if sys.version_info>=(3,10) else 1)" >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYCMD=%%P"
            goto PY_READY
        )
    )
)

rem ============================================================
rem 2) 以上都没有 → 自动下载便携版 Python（python.org 官方 embed 包）
rem ============================================================
echo [1/5] 未检测到系统 Python，将自动下载便携版 Python 3.11（约 11MB，仅首次需要）...
set "RUNTIME_DIR=%~dp0.runtime"
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
set "PYZIP=%RUNTIME_DIR%\python-embed.zip"
set "PYBASE=%RUNTIME_DIR%\python"
set "PYVER=3.11.9"
set "PYURL=https://www.python.org/ftp/python/%PYVER%/python-%PYVER%-embed-amd64.zip"

rem 便携版已就绪时直接复用（无需重新下载）
if exist "%PYBASE%\python.exe" (
    "%PYBASE%\python.exe" -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 (
        > "%RUNTIME_DIR%\launcher.py" echo import os, runpy, sys
        >> "%RUNTIME_DIR%\launcher.py" echo base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        >> "%RUNTIME_DIR%\launcher.py" echo sys.path.insert(0, base)
        >> "%RUNTIME_DIR%\launcher.py" echo runpy.run_path(os.path.join(base, "main.py"), run_name="__main__")
        set "PYCMD=%PYBASE%\python.exe"
        set "NO_VENV=1"
        set "SERVER_MAIN=%RUNTIME_DIR%\launcher.py"
        echo [1/5] 使用已就绪的便携版 Python
        goto PY_READY
    )
)

echo     下载中，请稍候（视网速而定）...
!PS_CMD! -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop';[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12;Invoke-WebRequest -UseBasicParsing -Uri '%PYURL%' -OutFile '%PYZIP%' -TimeoutSec 300"
if errorlevel 1 goto DL_FAIL

if exist "%PYBASE%" rmdir /s /q "%PYBASE%"
!PS_CMD! -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%PYZIP%' -DestinationPath '%PYBASE%' -Force"
if errorlevel 1 goto DL_FAIL

rem 启用 site（让第三方库目录 site-packages 生效）
!PS_CMD! -NoProfile -ExecutionPolicy Bypass -Command "$f=Get-ChildItem -LiteralPath '%PYBASE%' -Filter '*._pth'|Select-Object -First 1;if($f){(Get-Content -LiteralPath $f.FullName)-replace '^#\s*import site$','import site'|Set-Content -LiteralPath $f.FullName -Encoding ascii}"
if errorlevel 1 goto DL_FAIL

rem 安装 pip
echo     正在安装 pip...
!PS_CMD! -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop';[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12;Invoke-WebRequest -UseBasicParsing -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%RUNTIME_DIR%\get-pip.py' -TimeoutSec 120"
if errorlevel 1 goto DL_FAIL
"%PYBASE%\python.exe" "%RUNTIME_DIR%\get-pip.py" --no-warn-script-location
if errorlevel 1 goto DL_FAIL

rem 生成启动器：嵌入式 Python 不会自动把项目根目录加入 sys.path，
rem 由启动器显式插入（路径根据自身位置推算，随项目一起移动）
> "%RUNTIME_DIR%\launcher.py" echo import os, runpy, sys
>> "%RUNTIME_DIR%\launcher.py" echo base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
>> "%RUNTIME_DIR%\launcher.py" echo sys.path.insert(0, base)
>> "%RUNTIME_DIR%\launcher.py" echo runpy.run_path(os.path.join(base, "main.py"), run_name="__main__")

set "PYCMD=%PYBASE%\python.exe"
set "NO_VENV=1"
set "SERVER_MAIN=%RUNTIME_DIR%\launcher.py"
goto PY_READY

:DL_FAIL
echo.
echo [错误] 自动下载便携版 Python 失败，请手动安装：
echo   1. 打开 https://www.python.org/downloads/
echo   2. 安装 Python 3.10 或更高版本
echo   3. 安装时勾选 "Add python.exe to PATH"
echo   4. 重新运行本脚本
pause
exit /b 1

rem ============================================================
rem 3) 创建/复用项目虚拟环境（系统 Python 场景）
rem ============================================================
:PY_READY
echo [1/5] 使用 Python: !PYCMD!
!PYCMD! --version

if not defined NO_VENV (
    if not exist "%VENV_PY%" (
        echo [2/5] 首次运行：正在创建项目虚拟环境...
        !PYCMD! -m venv .venv >nul 2>nul
    )
    if exist "%VENV_PY%" (
        "%VENV_PY%" -c "import sys" >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYCMD=%VENV_PY%"
        ) else (
            echo [提示] 虚拟环境创建失败，将直接使用系统 Python 安装依赖。
        )
    )
)

rem ============================================================
rem 4) 检查并安装依赖（requirements.txt，含清华镜像源兜底）
rem ============================================================
echo [3/5] 检查依赖...
!PYCMD! -c "import fastapi,uvicorn,sqlalchemy,pydantic,docx,werkzeug,requests,reportlab,qrcode" >nul 2>nul
if !errorlevel! equ 0 goto DEPS_OK
echo [3/5] 依赖不全，正在安装（首次运行，需要联网，约 1-3 分钟）...
!PYCMD! -m pip install --disable-pip-version-check -r requirements.txt
if !errorlevel! neq 0 (
    echo     官方源安装失败，改用清华镜像源重试...
    !PYCMD! -m pip install --disable-pip-version-check -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
)
!PYCMD! -c "import fastapi,uvicorn,sqlalchemy,pydantic,docx,werkzeug,requests,reportlab,qrcode" >nul 2>nul
if !errorlevel! neq 0 goto INSTALL_FAIL
:DEPS_OK
echo [3/5] 依赖就绪。

rem ============================================================
rem 5) 启动服务并等待就绪
rem ============================================================
netstat -ano | findstr /c:":!APP_PORT! " | findstr "LISTENING" >nul 2>nul
if !errorlevel! equ 0 (
    echo [提示] 端口 !APP_PORT! 已被占用（可能已有实例在运行，稍后会自动探测）。
)
echo [4/5] 正在启动服务...
if not defined SERVER_MAIN set "SERVER_MAIN=main.py"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "APP_HOST=%APP_HOST%"
set "APP_PORT=%APP_PORT%"
start "MindGuard Server" /min cmd /k "chcp 65001>nul && ""!PYCMD!"" ""!SERVER_MAIN!"""

echo [5/5] 等待服务就绪（首次启动稍慢，请稍候）...
set /a tries=0
:HEALTH_LOOP
set /a tries+=1
!PS_CMD! -NoProfile -ExecutionPolicy Bypass -Command "try{$r=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:!APP_PORT!/api/health' -TimeoutSec 2;if($r.StatusCode -eq 200){exit 0}else{exit 1}}catch{exit 1}"
if !errorlevel! equ 0 goto HEALTH_OK
if !tries! geq 45 goto HEALTH_TIMEOUT
<nul set /p="."
ping -n 2 127.0.0.1 >nul
goto HEALTH_LOOP

:HEALTH_OK
echo.
echo ============================================================
echo   MindGuard 已启动！
echo   系统入口:  http://localhost:!APP_PORT!/
echo   管理后台:  http://localhost:!APP_PORT!/admin
echo   默认账号:  admin    默认密码: admin123
echo ============================================================
if not defined MG_NO_BROWSER start "" "http://localhost:!APP_PORT!/"
goto END

:HEALTH_TIMEOUT
echo.
echo [警告] 服务未在预期时间内就绪。
echo   请查看 "MindGuard Server" 窗口中的报错信息，或日志文件：
echo   %~dp0logs\mmhs.log
goto END

:END
echo.
echo 下次启动将直接使用已就绪的环境，无需再次安装。
echo 关闭 "MindGuard Server" 窗口即可停止服务。
echo.
pause
endlocal
