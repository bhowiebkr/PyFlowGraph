@echo off
echo ========================================
echo PyFlowGraph GUI Integration Test Suite
echo ========================================
echo.
echo Running GUI tests that open actual application windows...
echo Please do not interact with test windows during execution.
echo.

cd /d "%~dp0"

REM Ensure we're in the right directory
if not exist "src\main.py" (
    echo ERROR: Cannot find src\main.py
    echo Please run this script from the PyFlowGraph root directory
    pause
    exit /b 1
)

REM Run the GUI test suite
python tests\gui\test_full_gui_integration.py

echo.
echo GUI tests complete.
pause