@echo off
:: Quick Test Runner - Run the most important tests
:: This script runs the tests that identify the core issues

echo ================================================
echo PyFlowGraph Quick Test Runner
echo ================================================
echo Running the key tests to identify GUI/pin issues...
echo.

echo [1/2] Testing for specific GUI bugs (text_processing_pipeline.md)...
echo ================================================
python test_specific_gui_bugs.py
set gui_result=%errorlevel%
echo.

echo [2/2] Testing for pin creation bugs (root cause)...
echo ================================================
python test_pin_creation_bug.py
set pin_result=%errorlevel%
echo.

echo ================================================
echo TEST RESULTS SUMMARY
echo ================================================

if %gui_result%==0 (
    echo ✓ GUI Bug Tests: PASSED - GUI components are working correctly
) else (
    echo ✗ GUI Bug Tests: FAILED - Found GUI rendering issues
)

if %pin_result%==0 (
    echo ✓ Pin Creation Tests: PASSED - Pins are created properly
) else (
    echo ✗ Pin Creation Tests: FAILED - Found pin categorization bug ^(ROOT CAUSE^)
)

echo.
if %pin_result% neq 0 (
    echo DIAGNOSIS: The issue is pin categorization during markdown loading,
    echo not GUI rendering. Nodes have pins but they lack proper pin_direction
    echo attributes, which makes connections fail and GUI appear broken.
    echo.
    echo RECOMMENDATION: Fix pin direction assignment in markdown deserialization.
) else if %gui_result% neq 0 (
    echo DIAGNOSIS: Found GUI rendering issues that need investigation.
) else (
    echo STATUS: No major issues detected in this test run.
)

echo.
echo To run more comprehensive tests, use: run_tests.bat
echo.
