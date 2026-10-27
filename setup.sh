#!/bin/bash

# WhatsApp Automation Setup Script

echo "🚀 WhatsApp Web Campaign Automation - Setup"
echo "============================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $PYTHON_VERSION"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "   ⚠️  Warning: Python 3.11+ recommended (you have $PYTHON_VERSION)"
fi
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q
echo "   ✅ pip upgraded"
echo ""

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt -q
if [ $? -eq 0 ]; then
    echo "   ✅ All packages installed"
else
    echo "   ❌ Error installing packages"
    exit 1
fi
echo ""

# Install Playwright browser
echo "🌐 Installing Playwright Chromium browser..."
playwright install chromium
if [ $? -eq 0 ]; then
    echo "   ✅ Chromium browser installed"
else
    echo "   ❌ Error installing browser"
    exit 1
fi
echo ""

# Check for .env file
echo "🔧 Checking configuration..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
else
    echo "   ⚠️  .env file not found"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   ⚠️  IMPORTANT: Edit .env file with your Firebase credentials!"
fi
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads sessions/whatsapp
echo "   ✅ Directories ready"
echo ""

# Summary
echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure Firebase:"
echo "   - Go to https://console.firebase.google.com/"
echo "   - Create/select project"
echo "   - Enable Firestore Database"
echo "   - Download service account JSON"
echo ""
echo "2. Edit .env file:"
echo "   - nano .env"
echo "   - Add your Firebase credentials"
echo ""
echo "3. Start the application:"
echo "   - ./start.sh"
echo "   - OR: python app.py"
echo ""
echo "4. Open browser:"
echo "   - http://localhost:5000"
echo ""
echo "For detailed instructions, see README.md or QUICKSTART.md"
echo ""
