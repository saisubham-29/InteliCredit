#!/bin/bash
# INTELLI-CREDIT Quick Start Script

echo "=========================================="
echo "INTELLI-CREDIT Setup & Launch"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check for .env file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠ Please edit .env and add your GEMINI_API_KEY"
    echo "  Get your key from: https://makersuite.google.com/app/apikey"
else
    echo "✓ .env file exists"
fi

# Create storage directories
echo ""
echo "Creating storage directories..."
mkdir -p storage/models storage/cam storage/uploads
echo "✓ Storage directories created"

# Run tests
echo ""
echo "Running setup tests..."
python test_setup.py

# Ask if user wants to start server
echo ""
read -p "Start the server now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "=========================================="
    echo "Starting INTELLI-CREDIT Server..."
    echo "=========================================="
    echo ""
    echo "Dashboard will be available at: http://127.0.0.1:8000"
    echo "API docs will be available at: http://127.0.0.1:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    uvicorn api.main:app --reload
else
    echo ""
    echo "To start the server later, run:"
    echo "  source .venv/bin/activate"
    echo "  uvicorn api.main:app --reload"
    echo ""
fi
