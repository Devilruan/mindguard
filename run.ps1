# MindGuard Launcher - PowerShell ??????
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "============================================"
Write-Host "  MindGuard v1.2.0 - DEVELOPMENT MODE"
Write-Host "============================================"
Write-Host ""

# ?? python
try { $null = python --version 2>&1 } catch { Write-Host "[ERROR] Python not found."; pause; exit 1 }

# ????
Get-Process -Name python,mmhs -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

# ????
netstat -ano | findstr ":8000" | findstr "LISTEN" >nul
if ($LASTEXITCODE -eq 0) {
    Write-Host "[WARN] Port 8000 in use, freeing..."
    $pid8000 = (netstat -ano | findstr ":8000" | findstr "LISTEN").Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)[-1]
    Stop-Process -Id $pid8000 -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# ? .NET Process ??????? PowerShell ?????
$proc = [System.Diagnostics.Process]::new()
$proc.StartInfo.FileName = "python"
$proc.StartInfo.Arguments = "main.py"
$proc.StartInfo.WorkingDirectory = $PSScriptRoot
$proc.StartInfo.UseShellExecute = $false
$proc.StartInfo.CreateNoWindow = $false
$proc.Start() | Out-Null

Write-Host "[INFO] Starting server (PID: $($proc.Id))..."

# ???
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 500
    if (-not (Get-Process -Id $proc.Id -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] Server process died during startup."
        pause; exit 1
    }
    try {
        Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2 | Out-Null
        Write-Host ""
        Write-Host "============================================"
        Write-Host "  MindGuard is ready!"
        Write-Host "============================================"
        Write-Host ""
        Write-Host "  Homepage: http://localhost:8000"
        Write-Host "  Admin   : http://localhost:8000/admin"
        Write-Host ""
        Write-Host "  Admin login: admin / admin123"
        Write-Host ""
        Write-Host "  Keep this window open while using MindGuard."
        Write-Host "  Close this window to stop the server."
        Write-Host ""
        
        # ?????
        Start-Process "http://localhost:8000"
        
        # ???????????
        $proc.WaitForExit()
        
        if ($proc.ExitCode -ne 0) {
            Write-Host ""
            Write-Host "[WARN] Server exited with code $($proc.ExitCode)"
            pause
        }
        exit 0
    } catch {}
}

Write-Host "[ERROR] Server failed to start within 10 seconds."
pause