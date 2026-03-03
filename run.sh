#!/bin/bash
# Packrat — macOS launcher
# Usage: ./run.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Install deps if needed
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Launch
python3 main.py
