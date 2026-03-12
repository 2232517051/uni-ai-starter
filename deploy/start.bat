@echo off
REM ===========================================
REM Quick start script for uni-ai-starter backend (Windows)
REM ===========================================

cd /d "%~dp0..\backend"

if not exist .env (
    echo [ERROR] .env not found! Copy .env.example to .env and fill in your API keys.
    echo    copy .env.example .env
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt -q

echo Starting server...
python main.py

pause
