#!/usr/bin/env bash
# Run this file to install dependencies (first run only) and start the game.
# From a terminal: ./run.sh
# Or double-click it in a file manager that's configured to run .sh scripts.
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Python 3 was not found. Install it from https://www.python.org/downloads/ and try again."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Installing/updating dependencies..."
"$PYTHON" -m pip install --quiet -r "$DIR/requirements.txt"

echo "Starting Corey Chowda..."
"$PYTHON" "$DIR/main.py"
