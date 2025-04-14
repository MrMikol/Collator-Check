@echo off
python -c "import requests; requests.get('https://discord.com').raise_for_status()"
if %errorlevel% neq 0 (
    echo [ERROR] No internet connection
    exit /b 1
)
python check_collators.py --test