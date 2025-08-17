@echo off
:: Test Runner GUI Launcher
:: Launches the professional test runner GUI using the main app's virtual environment

echo ================================================
echo PyFlowGraph Test Runner GUI
echo ================================================
echo Starting professional test management interface...
echo.

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found at 'venv\'
    echo Please run the main application first to create the environment.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment and run test GUI
call venv\Scripts\activate.bat
python src\testing\test_runner_gui.py

:: Deactivate environment
call venv\Scripts\deactivate.bat

echo.
echo Test Runner GUI closed.
