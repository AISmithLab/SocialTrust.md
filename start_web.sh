#!/bin/bash

# SocialTrust Web Application Launcher

echo "======================================"
echo "  SocialTrust Web Application"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "Flask is not installed. Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Change to src directory
cd src

# Start the web application
echo "Starting SocialTrust Web Server..."
echo ""
echo "Once started, open your browser and go to:"
echo "  http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
