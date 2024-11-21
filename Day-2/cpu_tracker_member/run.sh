#!/bin/sh

## This code is coped from - https://syftbox-documentation.openmined.org/cpu-tracker-1
set -e

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Virtual environment created."
fi

. .venv/bin/activate

echo "Installing dependencies..."
pip install -U syftbox diffprivlib psutil --quiet
echo "Dependencies installed."

echo "Running CPU Tracker Member with $(python3 --version) at '$(which python3)'"
python3 main.py

deactivate
