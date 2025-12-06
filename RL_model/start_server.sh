#!/bin/bash

# Trading Model Server - Quick Start Script
# This script helps you set up and run the trading model server

echo "=========================================="
echo "   Trading Model Server - Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements_server.txt
echo "✓ Dependencies installed"

# Check if model exists
echo ""
if [ -f "FinRL_Trading_Results/trained_ppo_trading_model.zip" ]; then
    echo "✓ Trained model found"
else
    echo "⚠️  Warning: Trained model not found at FinRL_Trading_Results/trained_ppo_trading_model.zip"
    echo "   Please run the Jupyter notebook to train the model first."
fi

echo ""
echo "=========================================="
echo "   Server is ready to start!"
echo "=========================================="
echo ""
echo "Starting server on http://localhost:5000..."
echo ""
echo "Available endpoints:"
echo "  • http://localhost:5000/api/health"
echo "  • http://localhost:5000/api/model/info"
echo "  • http://localhost:5000/api/test (POST)"
echo "  • http://localhost:5000/api/predict (POST)"
echo ""
echo "Dashboard: Open dashboard.html in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Start the server
python3 trading_server.py
