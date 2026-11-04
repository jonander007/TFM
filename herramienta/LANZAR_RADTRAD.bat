@echo off
cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1
set OPENBLAS_NUM_THREADS=1
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
python RADTRAD_GUI.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo ================================================
    echo  ERROR al ejecutar RADTRAD_GUI.py
    echo  Revisa el mensaje de arriba
    echo ================================================
    pause
)
