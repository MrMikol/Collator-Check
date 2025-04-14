@echo off
cd /d "%~dp0"
if not exist "logs" mkdir logs

:loop
set timestamp=%date%_%time%
echo [%timestamp%] START >> logs\monitor.log

python check_collators.py >> logs\monitor.log 2>> logs\errors.log
if %errorlevel% neq 0 (
    echo [%timestamp%] ERROR >> logs\errors.log
    python check_collators.py --send-alert "Batch script encountered error"
)

timeout /t 3600 > nul
goto loop