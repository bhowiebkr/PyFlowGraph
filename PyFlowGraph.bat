@echo off
rem Starts PyFlowGraph with the Python in the venv folder.
rem Arguments are passed to src\main.py.

setlocal
cd /d "%~dp0"

set VENV_PYTHON=venv\Scripts\python.exe
set MAIN_SCRIPT=src\main.py

if not exist "%VENV_PYTHON%" (
    echo Error: %VENV_PYTHON% not found.
    echo Set up the venv first. CONTRIBUTING.md tells how.
    exit /b 1
)

if not exist "%MAIN_SCRIPT%" (
    echo Error: %MAIN_SCRIPT% not found.
    exit /b 1
)

"%VENV_PYTHON%" "%MAIN_SCRIPT%" %*
exit /b %errorlevel%
