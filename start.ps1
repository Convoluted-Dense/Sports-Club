# ========================================================
# SPORTS CLUB MEMBERSHIP & TOURNAMENT DBMS SYSTEM
# One-Click PowerShell Launcher
# ========================================================

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " SPORTS CLUB DBMS - MANAGEMENT COCKPIT & SQL STUDIO" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.8+ to run the local server." -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/2] Checking and initializing database..." -ForegroundColor Yellow
python "$PSScriptRoot\db_manager.py"

Write-Host "`n[2/2] Starting local web server on http://localhost:5000..." -ForegroundColor Green
python "$PSScriptRoot\app.py"
