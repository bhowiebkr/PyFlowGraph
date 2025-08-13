@echo off
echo Running GUI Loading Fix Test...
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the test
python tests\test_gui_loading_fix.py

echo.
echo Test completed. Press any key to exit...
pause > nul