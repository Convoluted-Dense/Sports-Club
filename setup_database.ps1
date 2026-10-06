# ============================================================================
# SPORTS CLUB MEMBERSHIP AND TOURNAMENT MANAGEMENT SYSTEM
# Automated Database Setup & Verification Script (PostgreSQL)
# ============================================================================

param (
    [string]$DbUser = "postgres",
    [string]$DbPassword = "SportsClub#2026!Pass",
    [string]$DbHost = "localhost",
    [int]$DbPort = 5432,
    [string]$DbName = "sports_club_db"
)

$ErrorActionPreference = "Stop"
$env:PGPASSWORD = $DbPassword

$psql = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
if (-not (Test-Path $psql)) {
    $psqlCmd = Get-Command psql -ErrorAction SilentlyContinue
    if ($psqlCmd) {
        $psql = $psqlCmd.Source
    } else {
        Write-Error "psql.exe not found in PATH or standard installation directory."
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " SPORTS CLUB MEMBERSHIP & TOURNAMENT DBMS - POSTGRESQL SETUP" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Step 1: Re-create Database
Write-Host "`n[1/4] Creating database '$DbName'..." -ForegroundColor Yellow
& $psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c "DROP DATABASE IF EXISTS $DbName;" | Out-Null
& $psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c "CREATE DATABASE $DbName;"
Write-Host "Database '$DbName' successfully created!" -ForegroundColor Green

# Step 2: Apply DDL Schema
Write-Host "`n[2/4] Applying 3NF Schema (Tables, Constraints, Indexes, Triggers, Views)..." -ForegroundColor Yellow
& $psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -f "$PSScriptRoot\schema.sql"
Write-Host "Schema applied successfully!" -ForegroundColor Green

# Step 3: Populate Data
Write-Host "`n[3/4] Populating database with 27 members, 6 clubs, diverse payments & matches..." -ForegroundColor Yellow
& $psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -f "$PSScriptRoot\populate_data.sql"
Write-Host "Data populated successfully!" -ForegroundColor Green

# Step 4: Verification Summary
Write-Host "`n[4/4] Verifying Table Row Counts and Status Distribution..." -ForegroundColor Yellow
& $psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -c @"
SELECT 'member' AS table_name, count(*) AS total_rows FROM member
UNION ALL SELECT 'club', count(*) FROM club
UNION ALL SELECT 'sport', count(*) FROM sport
UNION ALL SELECT 'facility', count(*) FROM facility
UNION ALL SELECT 'coach', count(*) FROM coach
UNION ALL SELECT 'membership_plan', count(*) FROM membership_plan
UNION ALL SELECT 'club_member', count(*) FROM club_member
UNION ALL SELECT 'payment', count(*) FROM payment
UNION ALL SELECT 'training_session', count(*) FROM training_session
UNION ALL SELECT 'tournament', count(*) FROM tournament
UNION ALL SELECT 'fixture', count(*) FROM fixture
UNION ALL SELECT 'team', count(*) FROM team;
"@

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " DATABASE SETUP COMPLETE & FULLY OPERATIONAL!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
