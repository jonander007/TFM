@echo off
rem TFM - zonas de emergencia KP-FHR en el puerto de Bilbao
cd /d "%~dp0"
python -m pip install -r requirements.txt
python PIPELINE.py
pause
