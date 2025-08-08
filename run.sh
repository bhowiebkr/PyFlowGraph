#!/bin/bash

# Set the script to exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Name of the virtual environment directory.
# Common names are 'venv', '.venv', 'env'.
VENV_DIR="venv"

# Name of the main python script to run.
PYTHON_SCRIPT="main.py"
# ---------------------

# Check if the virtual environment directory exists.
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment directory '$VENV_DIR' not found."
    echo "Please create it first, for example: python3 -m venv $VENV_DIR"
    exit 1
fi

# Activate the virtual environment.
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if the main python script exists.
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script '$PYTHON_SCRIPT' not found."
    # Deactivate the virtual environment before exiting.
    deactivate
    exit 1
fi

# Execute the python script.
# Any arguments passed to run.sh will be passed to main.py
# For example: ./run.sh arg1 arg2
echo "Running $PYTHON_SCRIPT..."
python "$PYTHON_SCRIPT" "$@"

# The script will automatically deactivate the venv when it exits.
# You can also add 'deactivate' here if you have cleanup commands to run after.
echo "Script finished."