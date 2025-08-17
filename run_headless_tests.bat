@echo off
echo ======================================
echo PyFlowGraph Headless Unit Test Suite
echo ======================================
echo.
echo Running fast headless tests (no GUI windows)...
echo.

cd /d "%~dp0"

REM Ensure we're in the right directory
if not exist "src\main.py" (
    echo ERROR: Cannot find src\main.py
    echo Please run this script from the PyFlowGraph root directory
    pause
    exit /b 1
)

REM Run headless tests
echo Running Node System Tests...
python tests\headless\test_node_system.py

echo.
echo Running Pin System Tests...
python tests\headless\test_pin_system.py

echo.
echo Running Connection System Tests...
python tests\headless\test_connection_system.py

echo.
echo Headless tests complete.
pause