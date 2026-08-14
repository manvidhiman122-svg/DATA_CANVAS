#!/bin/bash

# Quick Start Script for Data Canvas on macOS/Linux

echo ""
echo "========================================"
echo "  Data Canvas - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Install with: brew install python3 (macOS) or apt-get install python3 (Linux)"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if install was successful
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Run: pip install -r requirements.txt"
    exit 1
fi

# Run Streamlit app
echo ""
echo "========================================"
echo "  Starting Data Canvas..."
echo "  Open browser to: http://localhost:8501"
echo "  Press Ctrl+C to stop"
echo "========================================"
echo ""

streamlit run app.py
