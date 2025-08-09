@echo off
rem A Windows batch script to set up the environment and run the main Python application.

rem --- Configuration ---
set VENV_DIR=venv
set PYTHON_SCRIPT=main.py
rem ---------------------

rem Check if the virtual environment directory exists.
if not exist "%VENV_DIR%\" (
    echo Error: Virtual environment directory '%VENV_DIR%' not found.
    echo Please create it first, for example: python -m venv %VENV_DIR%
    exit /b 1
)

rem Activate the virtual environment.
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

rem Check if the main python script exists.
if not exist "%PYTHON_SCRIPT%" (
    echo Error: Python script '%PYTHON_SCRIPT%' not found.
    rem Deactivate the virtual environment before exiting.
    call deactivate
    exit /b 1
)

rem Execute the python script.
rem Any arguments passed to run.bat will be passed to main.py
rem For example: run.bat arg1 arg2
echo Running %PYTHON_SCRIPT%...
python "%PYTHON_SCRIPT%" %*

rem Deactivate the virtual environment after the script finishes.
call deactivate
echo Script finished.
