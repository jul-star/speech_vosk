@echo off
REM Quick 60-second speech recording
call .venv\Scripts\activate.bat
python -m src.speech_60
pause
