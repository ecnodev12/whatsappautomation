#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║       FIXING CHROMIUM CRASH - Upgrading Playwright           ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to project directory
cd /Users/apple/Desktop/whatsappautomation

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check current version
echo ""
echo "📦 Current Playwright version:"
pip show playwright | grep Version

# Upgrade Playwright
echo ""
echo "⬆️  Upgrading Playwright to latest version..."
echo "   This will download ~42MB, please be patient..."
pip install --upgrade playwright

# Install new Chromium
echo ""
echo "🌐 Installing new Chromium browser..."
playwright install chromium

# Check new version
echo ""
echo "✅ New Playwright version:"
pip show playwright | grep Version

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║               ✅ UPGRADE COMPLETE!                           ║"
echo "║                                                               ║"
echo "║   Now restart the server with: python app.py                 ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
