@echo off
cd /d "C:\Users\ezsto\marec-marketing-agent"
if exist database\leads.db del /f /q database\leads.db
call venv\Scripts\activate.bat
python main.py