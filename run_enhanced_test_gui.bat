@echo off
echo ==========================================
echo PyFlowGraph Enhanced Test Runner GUI
echo ==========================================
echo.
echo Starting enhanced test runner with:
echo - Organized test categories (Headless vs GUI)
echo - Category-specific timeouts and handling
echo - Visual test management and execution
echo.

cd /d "%~dp0"

REM Ensure we're in the right directory
if not exist "src\main.py" (
    echo ERROR: Cannot find src\main.py
    echo Please run this script from the PyFlowGraph root directory
    pause
    exit /b 1
)

REM Run the enhanced test runner GUI
python src\testing\enhanced_test_runner_gui.py

echo.
echo Enhanced test runner closed.
pause