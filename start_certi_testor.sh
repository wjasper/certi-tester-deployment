#!/bin/bash

# Determine script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to activate virtual environment
activate_venv () {
    if [ -f "$SCRIPT_DIR/certi_testor_deployement_env/bin/activate" ]; then
        # Unix-like (Linux, macOS)
        source "$SCRIPT_DIR/certi_testor_deployement_env/bin/activate"
    elif [ -f "$SCRIPT_DIR/certi_testor_deployement_env/Scripts/activate" ]; then
        # Windows
        source "$SCRIPT_DIR\certi_testor_deployement_env\Scripts\activate"
    else
        echo "Virtual environment not found."
        exit 1
    fi
}

# Activate virtual environment
activate_venv

# Change to script directory
cd "$SCRIPT_DIR"

# Run your Flask application
python3 app.py