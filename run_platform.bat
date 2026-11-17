@echo off
title TITAN MARKETS - CAPITAL INTELLIGENCE PLATFORM
color 0A

echo =====================================================================
echo    PROJECT TITAN - INSTITUTIONAL CAPITAL INTELLIGENCE PLATFORM
echo                Groww-Clean Modern Decision Cockpit
echo =====================================================================
echo.
echo [1/3] Verifying Python Environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in system PATH.
    pause
    exit /b 1
)

if not exist "data\lakehouse\cricket.duckdb" (
    echo [INFO] Initializing Cricket Lakehouse database...
    python scripts\reseed_cricket_lakehouse.py
)
if not exist "data\lakehouse\equities.duckdb" (
    echo [INFO] Initializing Equities Lakehouse database...
    python scripts\seed_universe.py
)

echo [2/3] Launching Cockpit Browser...
start "" http://127.0.0.1:8000

echo [3/3] Starting Local Uvicorn FastAPI Server on port 8000...
echo ---------------------------------------------------------------------
echo URL: http://127.0.0.1:8000
echo Engine: DuckDB Columnar Lakehouse + LightGBM + Cytoscape.js
echo Press [Ctrl + C] to shutdown server.
echo ---------------------------------------------------------------------
echo.

set PYTHONPATH=.
uvicorn src.backend.main:app --host 127.0.0.1 --port 8000 --reload

pause
