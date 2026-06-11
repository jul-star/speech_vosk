@echo off
REM 300-second (5-minute) speech recording
call .venv\Scripts\activate.bat
python -m src.speech_300
pause
