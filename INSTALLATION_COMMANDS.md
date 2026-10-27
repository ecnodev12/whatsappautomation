# 📦 Installation Commands Reference

Complete command reference for setting up WhatsApp Web Campaign Automation.

## 🍎 macOS / Linux Installation

### Quick Setup (Automated)

```bash
cd /Users/apple/Desktop/whatsappautomation
./setup.sh
```

### Manual Setup

```bash
# 1. Navigate to project directory
cd /Users/apple/Desktop/whatsappautomation

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install Python packages
pip install -r requirements.txt

# 6. Install Playwright Chromium browser
playwright install chromium

# 7. Install system dependencies (if needed)
playwright install-deps

# 8. Create .env file
cp .env.example .env
nano .env  # Edit with your Firebase credentials

# 9. Start the application
python app.py

# OR use the start script
./start.sh
```

## 🪟 Windows Installation

### Manual Setup

```cmd
REM 1. Navigate to project directory
cd C:\Users\YourUser\Desktop\whatsappautomation

REM 2. Create virtual environment
python -m venv venv

REM 3. Activate virtual environment
venv\Scripts\activate

REM 4. Upgrade pip
python -m pip install --upgrade pip

REM 5. Install Python packages
pip install -r requirements.txt

REM 6. Install Playwright Chromium browser
playwright install chromium

REM 7. Create .env file
copy .env.example .env
notepad .env

REM 8. Start the application
python app.py
```

## 🔧 Firebase Configuration

### Get Firebase Credentials

1. **Go to Firebase Console**
   ```
   https://console.firebase.google.com/
   ```

2. **Create or Select Project**
   - Project ID: `whatsapp-automation-a8d2d` (or your own)

3. **Enable Firestore**
   - Build > Firestore Database > Create database

4. **Generate Service Account**
   - Settings (⚙️) > Project settings
   - Service accounts tab
   - Generate new private key
   - Download JSON file

5. **Configure .env**
   - Copy values from downloaded JSON to `.env`
   - Ensure `private_key` keeps the `\n` characters

### Example .env Configuration

```env
FLASK_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

FIREBASE_PROJECT_ID=whatsapp-automation-a8d2d
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@whatsapp-automation-a8d2d.iam.gserviceaccount.com

MIN_DELAY_SECONDS=15
MAX_DELAY_SECONDS=30

PORT=5000
DEBUG=false
```

## 🐍 Python Version Check

```bash
# Check Python version (needs 3.11+)
python3 --version

# If you don't have Python 3.11+, install it:
# macOS (using Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv

# Windows
# Download from https://www.python.org/downloads/
```

## 🔍 Verify Installation

```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Check installed packages
pip list

# Check Playwright
playwright --version

# Test Python syntax
python -m py_compile app.py config.py firebase_service.py excel_service.py whatsapp_worker.py

# Test Flask (should show no errors)
python -c "from app import app; print('✅ Flask app loaded successfully')"
```

## 🚀 Running the Application

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux

# Start Flask
python app.py
```

### Production Mode (with Gunicorn)

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Run in background
gunicorn -w 4 -b 0.0.0.0:5000 app:app --daemon

# With logging
gunicorn -w 4 -b 0.0.0.0:5000 app:app --access-logfile access.log --error-logfile error.log
```

## 🧪 Testing the Setup

### 1. Test Firebase Connection

```python
# test_firebase.py
from firebase_service import FirebaseService

try:
    firebase = FirebaseService()
    print("✅ Firebase connected successfully!")
    print(f"Database: {firebase.db}")
except Exception as e:
    print(f"❌ Firebase error: {e}")
```

Run:
```bash
python test_firebase.py
```

### 2. Test Excel Service

```python
# test_excel.py
from excel_service import ExcelService

result = ExcelService.parse_excel('sample_contacts.csv')
if result['success']:
    print(f"✅ Parsed {result['total']} contacts")
    for contact in result['contacts'][:3]:
        print(f"  - {contact['name']}: {contact['phone']}")
else:
    print(f"❌ Error: {result['error']}")
```

### 3. Access Dashboard

```bash
# Start the app
python app.py

# Open in browser
open http://localhost:5000  # macOS
# OR
xdg-open http://localhost:5000  # Linux
# OR manually open in browser: http://localhost:5000
```

## 🛠️ Common Issues & Fixes

### Issue: "No module named 'flask'"

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

### Issue: "Playwright browser not found"

```bash
playwright install chromium
playwright install-deps  # Installs system dependencies
```

### Issue: "Firebase authentication failed"

- Check `.env` file exists and has correct values
- Ensure `FIREBASE_PRIVATE_KEY` has `\n` characters (not actual newlines)
- Verify Firestore is enabled in Firebase Console

### Issue: "Port 5000 already in use"

```bash
# Change port in .env
echo "PORT=8080" >> .env

# Or kill process using port 5000
lsof -ti:5000 | xargs kill -9  # macOS/Linux
```

### Issue: "Permission denied" on scripts

```bash
chmod +x setup.sh start.sh
```

## 📚 Additional Resources

- Flask Documentation: https://flask.palletsprojects.com/
- Playwright Documentation: https://playwright.dev/python/
- Firebase Admin SDK: https://firebase.google.com/docs/admin/setup
- Firestore Documentation: https://firebase.google.com/docs/firestore

## 🆘 Getting Help

If you encounter issues:

1. Check the console/terminal output for error messages
2. Review the QUICKSTART.md guide
3. Check README.md troubleshooting section
4. Verify all dependencies are installed
5. Check that .env file is properly configured

## ✅ Installation Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All packages installed from requirements.txt
- [ ] Playwright Chromium browser installed
- [ ] Firebase project created
- [ ] Firestore enabled
- [ ] Service account JSON downloaded
- [ ] .env file configured
- [ ] Application starts without errors
- [ ] Dashboard accessible at http://localhost:5000
- [ ] WhatsApp Web connects successfully

---

**Next Step:** See [QUICKSTART.md](QUICKSTART.md) for usage instructions.
