@echo off
echo ========================================
echo PyFlowGraph Professional Test Runner GUI
echo ========================================
echo.
echo Starting PySide6 test runner with visual interface...
echo.

cd /d "%~dp0"

REM Ensure we're in the right directory
if not exist "testing\test_tool.py" (
    echo ERROR: Cannot find testing\test_tool.py
    echo Please run this script from the PyFlowGraph root directory
    pause
    exit /b 1
)

REM Run the GUI test runner
python testing\test_tool.py

echo.
echo Test runner GUI closed.
pause