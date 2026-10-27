# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install packages
pip install -r requirements.txt

# Install browser
playwright install chromium
```

## Step 2: Configure Firebase

1. Go to https://console.firebase.google.com/
2. Create/select project: `whatsapp-automation-a8d2d`
3. Enable **Firestore Database**
4. Go to Project Settings > Service Accounts
5. Click **Generate new private key**
6. Download the JSON file

## Step 3: Create .env File

```bash
cp .env.example .env
```

Edit `.env` with your Firebase credentials from the JSON file:

```env
FLASK_SECRET_KEY=your-secret-key-change-this

# Copy these from your Firebase service account JSON
FIREBASE_PROJECT_ID=whatsapp-automation-a8d2d
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com

MIN_DELAY_SECONDS=15
MAX_DELAY_SECONDS=30
PORT=5000
DEBUG=false
```

## Step 4: Start the Application

```bash
python app.py
```

Or use the start script:

```bash
./start.sh
```

## Step 5: Open Dashboard

Open your browser:
```
http://localhost:5000
```

## Step 6: Connect WhatsApp

1. Click **"Connect to WhatsApp Web"**
2. Scan the QR code with your phone
3. Wait for green status ✅

## Step 7: Create Campaign & Upload Contacts

1. Create a new campaign
2. Use the sample `sample_contacts.csv` or create your own Excel file
3. Upload contacts
4. Click **Start** to begin sending!

## 📱 Sample Excel Format

```csv
name,phone,message
John Doe,1234567890,Hi John! This is a test.
Jane Smith,9876543210,Hello Jane! Special offer.
```

Or use a template:
```csv
name,phone
John Doe,1234567890
Jane Smith,9876543210
```

With template: `Hi {{name}}, this is EcnoDev...`

## ⚠️ Important Notes

- Phone numbers should include country code without `+`
- Example: `919876543210` (India), `1234567890` (US)
- Only send to contacts who expect messages
- The system adds 15-30 second delays between messages
- You can pause/resume/stop campaigns anytime

## 🆘 Quick Troubleshooting

**Can't install packages?**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Playwright browser not working?**
```bash
playwright install chromium
playwright install-deps  # Installs system dependencies
```

**Firebase errors?**
- Check that private key has `\n` characters
- Verify Firestore is enabled
- Check project ID matches

**Port already in use?**
Change PORT in `.env` to 8080 or another available port.

---

For detailed documentation, see [README.md](README.md)
