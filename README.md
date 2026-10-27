# WhatsApp Web Campaign Automation Dashboard

A production-ready WhatsApp Web campaign automation system built with Python Flask, Firebase Firestore, and Playwright.

## ⚠️ Important Notice

- This system uses **WhatsApp Web through browser automation** (NOT WhatsApp Business API or Cloud API)
- The user must manually scan the QR code once to authenticate
- This is intended for **legitimate outreach to contacts who expect messages**
- Do NOT use for spam or unsolicited messages
- Respects WhatsApp's terms of service

## 🚀 Features

- ✅ WhatsApp Web browser automation with persistent sessions
- ✅ Firebase Firestore for campaign and contact management
- ✅ Excel/CSV contact import with template support
- ✅ Real-time campaign monitoring dashboard
- ✅ Pause/Resume/Stop campaign controls
- ✅ Contact status tracking (pending/sent/failed)
- ✅ Configurable message delays
- ✅ Error handling and retry logic
- ✅ Responsive web interface

## 📋 Prerequisites

- Python 3.11 or higher
- Firebase account with Firestore enabled
- Modern web browser (Chromium will be installed by Playwright)

## 🛠️ Setup Instructions

### 1. Clone or Download the Project

```bash
cd /Users/apple/Desktop/whatsappautomation
```

### 2. Create Python Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Playwright Chromium Browser

```bash
playwright install chromium
```

This downloads the Chromium browser needed for WhatsApp Web automation.

### 5. Set Up Firebase

#### 5.1 Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select existing project
3. Enter project name (e.g., "whatsapp-automation-a8d2d")
4. Follow the setup wizard

#### 5.2 Enable Firestore Database

1. In Firebase Console, go to **Build > Firestore Database**
2. Click **Create database**
3. Choose **Start in production mode** (or test mode for development)
4. Select a location (choose closest to your region)
5. Click **Enable**

#### 5.3 Create Service Account

1. In Firebase Console, click the gear icon ⚙️ > **Project settings**
2. Go to **Service accounts** tab
3. Click **Generate new private key**
4. Save the downloaded JSON file securely (DO NOT commit to git)

The JSON file will look like:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com",
  ...
}
```

### 6. Configure Environment Variables

#### 6.1 Copy the example environment file:

```bash
cp .env.example .env
```

#### 6.2 Edit `.env` file with your values:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here-change-this

# Firebase Configuration (from the JSON file downloaded)
FIREBASE_PROJECT_ID=whatsapp-automation-a8d2d
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@whatsapp-automation-a8d2d.iam.gserviceaccount.com

# WhatsApp Automation Settings
MIN_DELAY_SECONDS=15
MAX_DELAY_SECONDS=30

# Server Configuration
PORT=5000
DEBUG=false
```

**Important Notes:**
- Copy the exact `private_key` value from your Firebase JSON file
- Keep the `\n` characters in the private key - they are important!
- Generate a secure random string for `FLASK_SECRET_KEY`
- Never commit the `.env` file to version control

#### 6.3 Generate a secure Flask secret key:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Use the output as your `FLASK_SECRET_KEY`.

### 7. Start the Flask Application

```bash
python app.py
```

You should see:
```
INFO:__main__:Starting Flask application on port 5000
INFO:__main__:Debug mode: False
 * Running on http://0.0.0.0:5000
```

### 8. Open the Dashboard

Open your web browser and go to:
```
http://localhost:5000
```

## 📱 Using the System

### Step 1: Connect to WhatsApp Web

1. Click **"Connect to WhatsApp Web"** button
2. A Chromium browser window will open
3. Scan the QR code with your phone (WhatsApp > Settings > Linked Devices)
4. Once logged in, the status indicator will turn green ✅

**Note:** The browser profile is saved in `sessions/whatsapp/`, so you only need to scan the QR code once.

### Step 2: Create a Campaign

1. Enter a campaign name (e.g., "Product Launch 2024")
2. Click **"Create Campaign"**

### Step 3: Upload Contacts

1. Prepare an Excel (.xlsx) or CSV file with these columns:
   - `name` - Contact name (optional)
   - `phone` - Phone number (required)
   - `message` - Message to send (optional if using template)

**Example Excel:**
```
name          | phone           | message
John Doe      | 1234567890      | Hi John, check our new product!
Jane Smith    | 9876543210      | Hi Jane, special offer for you!
```

**Or use a message template:**
```
Message Template: "Hi {{name}}, this is EcnoDev. We wanted to share something with you..."
```

2. Select your campaign from dropdown
3. Upload the Excel/CSV file
4. (Optional) Add a message template with `{{name}}` placeholder
5. Click **"Upload Contacts"**

### Step 4: Start the Campaign

1. Click on the campaign card to open details
2. Review the contacts and stats
3. Click **"▶️ Start"** button
4. The system will automatically send messages with delays between each

### Campaign Controls

- **▶️ Start** - Begin sending messages
- **⏸️ Pause** - Temporarily pause (can resume later)
- **▶️ Resume** - Continue from where paused
- **⏹️ Stop** - Permanently stop campaign

### Real-time Monitoring

The dashboard automatically updates every 2-3 seconds showing:
- Total contacts
- Messages sent
- Failed messages
- Pending messages
- Progress bar
- Individual contact statuses

## 📊 Phone Number Format

Phone numbers should include country code without `+`:

- ✅ Correct: `1234567890` or `919876543210`
- ❌ Avoid: `+91-98765-43210` (will be auto-cleaned)

The system automatically removes:
- Spaces
- Dashes `-`
- Plus sign `+`
- Parentheses `()` 
- Other non-numeric characters

## 🔧 Configuration

### Adjust Message Delays

Edit `.env` file:

```env
MIN_DELAY_SECONDS=20    # Minimum delay between messages
MAX_DELAY_SECONDS=40    # Maximum delay between messages
```

These delays help maintain natural sending patterns.

### Change Port

```env
PORT=8080
```

Then restart the application.

## 📁 Project Structure

```
whatsappautomation/
├── app.py                  # Main Flask application
├── whatsapp_worker.py      # WhatsApp automation logic
├── firebase_service.py     # Firebase/Firestore operations
├── excel_service.py        # Excel/CSV parsing
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .env.example           # Example environment file
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── templates/
│   └── index.html         # Dashboard HTML
├── static/
│   ├── style.css          # Dashboard styles
│   └── app.js             # Dashboard JavaScript
├── uploads/               # Temporary file uploads
└── sessions/
    └── whatsapp/          # Browser session data
```

## 🗃️ Firestore Data Structure

### Collections

**campaigns** (collection)
```
{
  name: "Campaign Name",
  status: "draft|running|paused|completed|stopped",
  total: 100,
  sent: 45,
  failed: 5,
  pending: 50,
  created_at: Timestamp,
  started_at: Timestamp,
  completed_at: Timestamp
}
```

**campaigns/{campaign_id}/contacts** (subcollection)
```
{
  name: "John Doe",
  phone: "1234567890",
  message: "Hi John...",
  status: "pending|sending|sent|failed",
  error: null | "Error message",
  sent_at: Timestamp,
  attempts: 0
}
```

## 🛡️ Security Best Practices

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use strong FLASK_SECRET_KEY** - Generate with `secrets.token_hex(32)`
3. **Keep Firebase credentials secure** - Don't share service account JSON
4. **Enable Firestore security rules** - Restrict access in production
5. **Use HTTPS in production** - Deploy behind reverse proxy (nginx/Apache)
6. **Limit file upload sizes** - Already set to 16MB max
7. **Validate all inputs** - System includes input validation

### Recommended Firestore Security Rules

In Firebase Console > Firestore Database > Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only allow server-side access
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

This ensures only your backend (with service account) can access Firestore.

## 🐛 Troubleshooting

### "Module not found" errors

```bash
pip install -r requirements.txt --force-reinstall
```

### Playwright browser not working

```bash
playwright install chromium
```

### Firebase authentication errors

- Check that `.env` file has correct values from Firebase JSON
- Ensure `FIREBASE_PRIVATE_KEY` includes `\n` characters
- Verify Firestore is enabled in Firebase Console

### WhatsApp QR code doesn't load

- Check internet connection
- Wait 30 seconds for page to load
- Try clicking "Connect to WhatsApp Web" again
- Clear `sessions/whatsapp/` folder and re-scan

### Messages not sending

- Verify you're logged into WhatsApp Web (green status indicator)
- Check that phone numbers are valid (minimum 10 digits)
- Ensure contacts have WhatsApp accounts
- Check console logs for specific errors

### Port already in use

Change port in `.env`:
```env
PORT=8080
```

## 📝 Excel Template Example

Create an Excel file with these columns:

| name       | phone      | message                                    |
|------------|------------|--------------------------------------------|
| John Doe   | 1234567890 | Hi John, check our new product!           |
| Jane Smith | 9876543210 | Hi Jane, special offer for you!           |
| Bob Wilson | 5555551234 | Hi Bob, limited time discount available!  |

**Or use message template:**

| name       | phone      |
|------------|------------|
| John Doe   | 1234567890 |
| Jane Smith | 9876543210 |

With template: `Hi {{name}}, this is EcnoDev. We wanted to share something with you...`

## 🚀 Production Deployment

### Using Gunicorn (recommended for production)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker (optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps

COPY . .
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t whatsapp-automation .
docker run -p 5000:5000 --env-file .env whatsapp-automation
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## ⚖️ Legal & Compliance

- ✅ Use only for legitimate business purposes
- ✅ Send messages only to contacts who expect them
- ✅ Comply with WhatsApp Terms of Service
- ✅ Follow local spam and privacy laws (CAN-SPAM, GDPR, etc.)
- ❌ Do NOT use for spam or unsolicited marketing
- ❌ Do NOT attempt to bypass rate limits
- ❌ Do NOT use for automated bots

## 🤝 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Flask/Playwright/Firebase documentation
3. Check browser console and server logs

## 📄 License

This project is provided as-is for educational and legitimate business use only.

---

**Built with ❤️ using Flask, Firebase, and Playwright**
