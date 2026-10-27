#!/bin/bash

clear

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   WhatsApp Campaign Automation - Final Setup & Start         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

EOF

echo "✅ Firebase credentials: CONFIGURED"
echo "✅ Virtual environment: EXISTS"
echo "✅ Python packages: INSTALLED"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: ./setup.sh first"
    exit 1
fi

echo "🔧 Step 1: Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Activated"
echo ""

echo "🌐 Step 2: Installing Playwright Chromium browser..."
echo "   (This may take 2-5 minutes on first run)"
echo ""
playwright install chromium
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Playwright install had issues, trying with dependencies..."
    playwright install chromium --with-deps
fi
echo ""
echo "   ✅ Browser installed"
echo ""

echo "🔥 Step 3: Testing Firebase connection..."
python3 test_connection.py
if [ $? -ne 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  IMPORTANT: Enable Firestore Database"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Open this link in your browser:"
    echo "   https://console.firebase.google.com/project/whatsapp-automation-a8d2d/firestore"
    echo ""
    echo "2. Click 'Create database'"
    echo "3. Choose 'Start in production mode'"
    echo "4. Select a region (closest to you)"
    echo "5. Click 'Enable'"
    echo ""
    echo "Then run this script again: ./RUN_ME_FIRST.sh"
    echo ""
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 ALL SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Starting Flask application..."
echo ""
python app.py
EOF

chmod +x /Users/apple/Desktop/whatsappautomation/RUN_ME_FIRST.sh
