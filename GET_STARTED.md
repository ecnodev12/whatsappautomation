# 🎉 Get Started with WhatsApp Web Campaign Automation

Welcome! This guide will help you get your WhatsApp campaign automation system running in minutes.

## 📋 What You'll Need

Before starting, make sure you have:
- [ ] Python 3.11 or higher installed
- [ ] Internet connection
- [ ] A smartphone with WhatsApp installed
- [ ] 15 minutes of time

## 🚀 Step-by-Step Setup

### Step 1: Run the Setup Script (Easiest)

Open Terminal and run:

```bash
cd /Users/apple/Desktop/whatsappautomation
./setup.sh
```

This will:
- ✅ Create a Python virtual environment
- ✅ Install all required packages
- ✅ Install Playwright Chromium browser
- ✅ Create a `.env` file template

**If you prefer manual setup**, see [INSTALLATION_COMMANDS.md](INSTALLATION_COMMANDS.md)

---

### Step 2: Set Up Firebase (5 minutes)

#### 2.1: Create Firebase Project

1. Go to: https://console.firebase.google.com/
2. Click **"Add project"** or use existing
3. Enter project name (or use: `whatsapp-automation-a8d2d`)
4. Follow the wizard (disable Google Analytics if not needed)
5. Click **"Create project"**

#### 2.2: Enable Firestore Database

1. In your Firebase project, click **"Build"** in left menu
2. Click **"Firestore Database"**
3. Click **"Create database"**
4. Choose **"Start in production mode"** (or test mode for development)
5. Select your region (choose closest to you)
6. Click **"Enable"**

#### 2.3: Get Your Service Account Credentials

1. Click the **gear icon (⚙️)** in top left
2. Click **"Project settings"**
3. Go to **"Service accounts"** tab
4. Click **"Generate new private key"**
5. Click **"Generate key"** in the popup
6. A JSON file will download - **keep it safe!**

The downloaded JSON looks like:
```json
{
  "type": "service_account",
  "project_id": "whatsapp-automation-a8d2d",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIE...==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@whatsapp-automation-a8d2d.iam.gserviceaccount.com",
  ...
}
```

---

### Step 3: Configure Your .env File

1. **Open the .env file:**
   ```bash
   nano .env
   # OR
   open -e .env  # Opens in TextEdit
   ```

2. **Fill in the values from your Firebase JSON:**

   ```env
   # Generate a random secret key
   FLASK_SECRET_KEY=your-random-secret-key-here
   
   # From Firebase JSON file:
   FIREBASE_PROJECT_ID=whatsapp-automation-a8d2d
   FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR_FULL_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n
   FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@whatsapp-automation-a8d2d.iam.gserviceaccount.com
   
   # Message delays (in seconds)
   MIN_DELAY_SECONDS=15
   MAX_DELAY_SECONDS=30
   
   # Server settings
   PORT=5000
   DEBUG=false
   ```

3. **Generate a secure Flask secret key:**
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copy the output and use it as `FLASK_SECRET_KEY`

4. **Important:** Make sure the `FIREBASE_PRIVATE_KEY` includes the `\n` characters (NOT actual line breaks)

5. **Save the file:**
   - If using nano: Press `Ctrl+X`, then `Y`, then `Enter`
   - If using TextEdit: Press `Cmd+S`

---

### Step 4: Start the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Start Flask
python app.py
```

Or simply use:
```bash
./start.sh
```

You should see:
```
INFO:__main__:Starting Flask application on port 5000
 * Running on http://0.0.0.0:5000
```

---

### Step 5: Open the Dashboard

Open your web browser and go to:
```
http://localhost:5000
```

You should see the WhatsApp Campaign Dashboard! 🎉

---

### Step 6: Connect to WhatsApp Web

1. **Click "Connect to WhatsApp Web"** button
2. A Chromium browser window will open
3. **WhatsApp Web QR code** will appear
4. **On your phone:**
   - Open WhatsApp
   - Tap the three dots (⋮) or Settings
   - Select **"Linked Devices"**
   - Tap **"Link a Device"**
   - Scan the QR code on your computer
5. **Wait for login** - status will turn green ✅

**Note:** You only need to scan the QR code once! The session is saved.

---

### Step 7: Create Your First Campaign

1. **Enter a campaign name** (e.g., "Test Campaign")
2. Click **"Create Campaign"**
3. Campaign appears in the list below ✅

---

### Step 8: Prepare Your Contact List

Create an Excel (.xlsx) or CSV file with these columns:

#### Option A: With Individual Messages

| name       | phone      | message                           |
|------------|------------|-----------------------------------|
| John Doe   | 1234567890 | Hi John! Test message.           |
| Jane Smith | 9876543210 | Hello Jane! Special offer.       |

#### Option B: With Template (Recommended)

| name       | phone      |
|------------|------------|
| John Doe   | 1234567890 |
| Jane Smith | 9876543210 |

Then use message template:
```
Hi {{name}}, this is a test message from our system!
```

**Phone Number Format:**
- Include country code (no + sign)
- Examples: `1234567890` (US), `919876543210` (India)
- System auto-removes spaces, dashes, and special characters

**Sample File Included:** Use `sample_contacts.csv` for testing!

---

### Step 9: Upload Contacts

1. **Select your campaign** from the dropdown
2. **Choose your Excel/CSV file**
3. (Optional) Add a **message template** with `{{name}}` placeholder
4. Click **"Upload Contacts"**
5. Review the success message and any warnings

---

### Step 10: Start Your Campaign

1. **Click on your campaign** card to open details
2. Review:
   - Total contacts
   - Contact list
   - Messages to be sent
3. Click **"▶️ Start"** button
4. Watch the progress bar! ⚡

The system will:
- ✅ Send messages one by one
- ✅ Wait 15-30 seconds between messages
- ✅ Update status in real-time
- ✅ Handle errors gracefully

---

## 🎮 Dashboard Controls

### Campaign Actions

- **▶️ Start** - Begin sending messages
- **⏸️ Pause** - Pause temporarily (can resume)
- **▶️ Resume** - Continue from where you paused
- **⏹️ Stop** - Permanently stop campaign

### Contact Filters

- **All** - Show all contacts
- **Pending** - Contacts waiting to be sent
- **Sent** - Successfully sent messages
- **Failed** - Messages that failed (with error details)

### Real-Time Updates

The dashboard automatically refreshes every 2-3 seconds to show:
- Messages sent
- Failed messages
- Remaining contacts
- Progress percentage

---

## 💡 Pro Tips

### Testing First
```bash
# Test with 2-3 contacts first
# Use your own phone number to verify
# Check message formatting
```

### Phone Number Tips
- Always include country code
- Test with known WhatsApp numbers
- Invalid numbers will be marked as failed

### Message Templates
```
Hi {{name}}, this is EcnoDev.

We wanted to share something exciting with you!

Check out: https://example.com

Best regards,
Team
```

### Monitoring
- Keep the dashboard open to monitor progress
- Check failed messages for issues
- Stop campaign if seeing many errors

---

## ❓ Troubleshooting

### "Firebase authentication failed"
- Check `.env` file exists
- Verify all Firebase credentials are correct
- Ensure `FIREBASE_PRIVATE_KEY` has `\n` characters

### "WhatsApp QR code won't load"
- Wait 30 seconds for page to load
- Check internet connection
- Try clicking "Connect" again

### "Messages not sending"
- Verify green status indicator (logged in)
- Check phone numbers are valid
- Ensure contacts have WhatsApp

### "Port 5000 already in use"
- Change `PORT=8080` in `.env` file
- Or kill the process: `lsof -ti:5000 | xargs kill -9`

### "Module not found" errors
- Activate virtual environment: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

---

## 📚 Next Steps

### Learn More
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick reference
- [INSTALLATION_COMMANDS.md](INSTALLATION_COMMANDS.md) - All commands

### Advanced Usage
- Configure message delays in `.env`
- Set up production deployment
- Add custom message templates
- Integrate with your CRM

### Security
- Keep `.env` file secure (never commit to git)
- Use strong `FLASK_SECRET_KEY`
- Enable Firestore security rules in production
- Monitor campaign activity

---

## ✅ Success Checklist

- [x] Python 3.11+ installed
- [x] Virtual environment created (`venv/`)
- [x] All packages installed
- [x] Playwright browser installed
- [x] Firebase project created
- [x] Firestore database enabled
- [x] Service account JSON downloaded
- [x] `.env` file configured
- [x] Flask application started
- [x] Dashboard accessible at http://localhost:5000
- [x] WhatsApp Web connected (green status)
- [x] Test campaign created
- [x] Contacts uploaded
- [x] First message sent successfully! 🎉

---

## 🎊 Congratulations!

You've successfully set up your WhatsApp Web campaign automation system!

**Remember:**
- ✅ Only send to contacts who know you
- ✅ Use for legitimate business purposes
- ✅ Respect WhatsApp's terms of service
- ✅ Monitor your campaigns
- ✅ Stop if errors occur

Need help? Check the troubleshooting sections in:
- This file (above)
- [README.md](README.md)
- [QUICKSTART.md](QUICKSTART.md)

---

**Built with ❤️ using Flask, Firebase, and Playwright**

Happy campaigning! 📱✨
