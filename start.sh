#!/bin/bash

# WhatsApp Automation Quick Start Script

echo "🚀 WhatsApp Web Campaign Automation"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup first:"
    echo ""
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo "  playwright install chromium"
    echo ""
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file from .env.example:"
    echo ""
    echo "  cp .env.example .env"
    echo "  # Edit .env with your Firebase credentials"
    echo ""
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Start Flask application
echo "🌐 Starting Flask application..."
echo ""
python app.py
