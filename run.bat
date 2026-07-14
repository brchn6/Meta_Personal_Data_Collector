@echo off
cd /d "%~dp0"

echo.
echo   ========================================================
echo      Meta Personal Data Collector
echo      One-click launcher
echo   ========================================================
echo.

rem --- 1. Install uv if missing -----------------------------------------
where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [DOWNLOADING] Installing uv (package manager^)...
    powershell -c "& { Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -OutFile uv-install.ps1; .\uv-install.ps1; del uv-install.ps1 }"
    rem Add uv to PATH for this session
    set "PATH=%USERPROFILE%\.cargo\bin;%USERPROFILE%\.local\bin;%PATH%"
)

where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Failed to install uv automatically.
    echo         Please install it from:  https://docs.astral.sh/uv/#installation
    pause
    exit /b 1
)

rem --- 2. Install dependencies ------------------------------------------
echo [INSTALLING] Dependencies...
call uv sync >nul

rem --- 3. Launch the app ------------------------------------------------
echo [LAUNCHING] Opening your browser...
start "" http://localhost:8501
call uv run streamlit run src/fb_image_extractor/app.py

pause
