@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo PyFlowGraph Local Build Script
echo ===============================================
echo.

REM Check if we're in the correct directory
if not exist "src\main.py" (
    echo ERROR: main.py not found in src directory
    echo Please run this script from the PyFlowGraph root directory
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    echo Please run this script from the PyFlowGraph root directory
    pause
    exit /b 1
)

echo [1/6] Checking prerequisites...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or later
    pause
    exit /b 1
)

REM Check if zstd is available (needed for runtime download)
zstd --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: zstd not found. You may need to install it for Python runtime download.
    echo You can install it with: choco install zstandard
    echo Or download manually from: https://facebook.github.io/zstd/
    echo Continuing without zstd - will try PowerShell for decompression...
)

echo [2/6] Installing/updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [3/6] Preparing Portable Python Runtime...

REM Check if python_runtime already exists
if exist "python_runtime" (
    echo Python runtime already exists, skipping download...
    goto :build_app
)

echo Downloading Python runtime (this may take a while)...
set "PYTHON_URL=https://github.com/astral-sh/python-build-standalone/releases/download/20250808/cpython-3.11.13+20250808-x86_64-pc-windows-msvc-pgo-full.tar.zst"

REM Download using PowerShell with better error handling
powershell -Command "try { Write-Host 'Downloading Python runtime...'; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile 'python-standalone.tar.zst' -UseBasicParsing; Write-Host 'Download completed.' } catch { Write-Host 'ERROR: Failed to download Python runtime'; Write-Host $_.Exception.Message; exit 1 }"
if errorlevel 1 goto :error

REM Verify download was successful
if not exist "python-standalone.tar.zst" (
    echo ERROR: Download failed - python-standalone.tar.zst not found
    goto :error
)

echo Decompressing Python runtime...
zstd -d python-standalone.tar.zst -o python-standalone.tar >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to decompress runtime with zstd
    echo Please install zstd using one of these methods:
    echo   choco install zstandard
    echo   winget install Facebook.zstd
    echo   scoop install zstd
    echo Or download from: https://facebook.github.io/zstd/
    goto :error
)

REM Verify decompression was successful
if not exist "python-standalone.tar" (
    echo ERROR: Decompression failed - python-standalone.tar not found
    goto :error
)

echo Extracting Python runtime...
tar -xf python-standalone.tar
if errorlevel 1 (
    echo ERROR: Failed to extract tar file
    goto :error
)

REM Verify extraction was successful
if not exist "python\install" (
    echo ERROR: Extraction failed - python\install directory not found
    goto :error
)

echo Moving Python runtime to final location...
if not exist "python_runtime" mkdir python_runtime
echo Copying Python runtime files with all subdirectories...
robocopy "python\install" "python_runtime" /E /NP /NFL /NDL
if errorlevel 8 (
    echo ERROR: Failed to copy Python runtime files
    goto :error
)

REM Verify critical directories exist
if not exist "python_runtime\Lib" (
    echo ERROR: Python runtime missing Lib directory - extraction incomplete
    echo Contents of python_runtime:
    dir "python_runtime" /B
    goto :error
)

REM Clean up temporary files
if exist "python" rmdir /s /q "python" >nul 2>&1
if exist "python-standalone.tar.zst" del "python-standalone.tar.zst" >nul 2>&1
if exist "python-standalone.tar" del "python-standalone.tar" >nul 2>&1

echo Python runtime prepared successfully.

:build_app
echo [4/6] Building application with Nuitka...

REM Create builds directory if it doesn't exist
if not exist "builds" mkdir builds

REM Clean previous build
if exist "builds\NodeEditor_Build" (
    echo Cleaning previous build...
    rmdir /s /q "builds\NodeEditor_Build"
    if exist "builds\NodeEditor_Build" (
        echo ERROR: Could not remove previous build directory
        goto :error
    )
)

echo Running Nuitka build (this will take several minutes)...
if not exist "src" (
    echo ERROR: src directory not found
    goto :error
)

cd src
python -m nuitka ^
  --standalone ^
  --enable-plugin=pyside6 ^
  --include-qt-plugins=platforms ^
  --output-dir=../builds/NodeEditor_Build ^
  --output-filename=PyFlowGraph.exe ^
  --nofollow-import-to=tkinter,unittest,setuptools,pip,wheel ^
  --windows-console-mode=disable ^
  --remove-output ^
  --lto=yes ^
  --include-data-dir=../examples=examples ^
  --include-data-dir=resources=resources ^
  --include-data-file=../dark_theme.qss=dark_theme.qss ^
  --assume-yes-for-downloads ^
  main.py

set NUITKA_RESULT=%ERRORLEVEL%
cd ..

if %NUITKA_RESULT% neq 0 (
    echo ERROR: Nuitka build failed with exit code %NUITKA_RESULT%
    goto :error
)

echo [5/6] Copying Python runtime to build...

set "DIST_DIR=builds\NodeEditor_Build\main.dist"

if not exist "%DIST_DIR%" (
    echo ERROR: Expected Nuitka output directory not found: %DIST_DIR%
    echo Available directories in builds\NodeEditor_Build:
    if exist "builds\NodeEditor_Build" dir "builds\NodeEditor_Build" /B
    goto :error
)

if not exist "%DIST_DIR%\PyFlowGraph.exe" (
    echo ERROR: PyFlowGraph.exe not found in build output
    echo Contents of %DIST_DIR%:
    dir "%DIST_DIR%" /B
    goto :error
)

echo Copying python_runtime to build directory...
if not exist "python_runtime" (
    echo ERROR: python_runtime directory not found
    goto :error
)

robocopy "python_runtime" "%DIST_DIR%\python_runtime" /E /NP /NFL /NDL >nul 2>&1
if errorlevel 8 (
    echo ERROR: Failed to copy Python runtime to build directory
    goto :error
)

echo [6/6] Finalizing build...

REM Get current timestamp for version using PowerShell with error handling
for /f "tokens=*" %%i in ('powershell -Command "try { Get-Date -Format 'yyyyMMdd-HHmmss' } catch { 'unknown' }"') do set "timestamp=%%i"

if "%timestamp%"=="unknown" (
    echo WARNING: Could not get timestamp, using default name
    set "timestamp=build"
)

echo Organizing build in builds directory...

set "FINAL_DIR=builds\PyFlowGraph-Windows-local-%timestamp%"

REM Remove existing final directory if it exists
if exist "%FINAL_DIR%" (
    echo Removing existing build: %FINAL_DIR%
    rmdir /s /q "%FINAL_DIR%"
)

REM Move the build directory to final location
move "%DIST_DIR%" "%FINAL_DIR%" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to rename build directory
    echo Source: %DIST_DIR%
    echo Target: %FINAL_DIR%
    goto :error
)

REM Verify the final executable exists
if not exist "%FINAL_DIR%\PyFlowGraph.exe" (
    echo ERROR: PyFlowGraph.exe not found in final build directory
    goto :error
)

echo.
echo ===============================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ===============================================
echo.
echo All builds are organized in the 'builds' folder
echo Build location: %FINAL_DIR%
echo Executable: %FINAL_DIR%\PyFlowGraph.exe
echo.
echo Contents of build directory:
dir "%FINAL_DIR%" /B
echo.

REM Build completed - showing final information
echo To run PyFlowGraph: %FINAL_DIR%\PyFlowGraph.exe

echo Build complete.
exit /b 0

:error
echo.
echo ===============================================
echo BUILD FAILED!
echo ===============================================
echo Please check the error messages above and try again.
echo.
echo Common solutions:
echo - Install zstd: choco install zstandard
echo - Install Python 3.11+
echo - Install Visual Studio Build Tools
echo - Check internet connection for downloads
echo.
pause
exit /b 1