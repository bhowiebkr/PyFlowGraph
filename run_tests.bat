@echo off
:: PyFlowGraph Test Runner
:: Helper script to run various GUI and pin creation tests

echo ================================================
echo PyFlowGraph Test Suite Runner
echo ================================================
echo.

:menu
echo Select which tests to run:
echo.
echo 1. Quick GUI Bug Detection (recommended)
echo 2. Pin Creation Bug Test (root cause)
echo 3. GUI Rendering Tests (visual verification)
echo 4. Comprehensive GUI Tests (full suite)
echo 5. All Tests (run everything)
echo 6. Original Execution Flow Test
echo.
echo 0. Exit
echo.
set /p choice="Enter your choice (0-6): "

if "%choice%"=="0" goto :exit
if "%choice%"=="1" goto :quick
if "%choice%"=="2" goto :pin_test
if "%choice%"=="3" goto :rendering
if "%choice%"=="4" goto :comprehensive
if "%choice%"=="5" goto :all_tests
if "%choice%"=="6" goto :original
goto :invalid

:quick
echo.
echo ================================================
echo Running Quick GUI Bug Detection Tests
echo ================================================
echo This tests the specific issues you reported
echo.
python test_specific_gui_bugs.py
echo.
pause
goto :menu

:pin_test
echo.
echo ================================================
echo Running Pin Creation Bug Tests
echo ================================================
echo This identifies the root cause of the issues
echo.
python test_pin_creation_bug.py
echo.
pause
goto :menu

:rendering
echo.
echo ================================================
echo Running GUI Rendering Tests
echo ================================================
echo This verifies visual GUI components work correctly
echo.
python test_gui_rendering.py
echo.
pause
goto :menu

:comprehensive
echo.
echo ================================================
echo Running Comprehensive GUI Tests
echo ================================================
echo This is the full GUI loading test suite
echo.
python test_gui_loading.py
echo.
pause
goto :menu

:all_tests
echo.
echo ================================================
echo Running ALL Tests
echo ================================================
echo This will run every test file in sequence
echo.

echo --- Basic GUI Loading Tests ---
python test_gui_loading_bugs.py
echo.

echo --- Specific GUI Bug Tests ---
python test_specific_gui_bugs.py
echo.

echo --- GUI Rendering Tests ---
python test_gui_rendering.py
echo.

echo --- Pin Creation Bug Tests ---
python test_pin_creation_bug.py
echo.

echo --- Comprehensive GUI Tests ---
python test_gui_loading.py
echo.

echo --- Original Execution Flow Test ---
python test_execution_flow.py
echo.

echo ================================================
echo All tests completed!
echo ================================================
pause
goto :menu

:original
echo.
echo ================================================
echo Running Original Execution Flow Test
echo ================================================
echo This is the original test from the codebase
echo.
python test_execution_flow.py
echo.
pause
goto :menu

:invalid
echo.
echo Invalid choice. Please select 0-6.
echo.
goto :menu

:exit
echo.
echo Exiting test runner...
exit /b 0