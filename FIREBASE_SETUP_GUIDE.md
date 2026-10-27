# 🔥 Firebase Admin SDK Setup Guide

## Your Firebase Project

**Project ID:** `whatsapp-automation-a8d2d`  
**Project URL:** https://console.firebase.google.com/project/whatsapp-automation-a8d2d

---

## ⚠️ Important: Web SDK vs Admin SDK

You already have the **Firebase Web SDK** configuration (for JavaScript frontend apps), but this Python backend project needs the **Firebase Admin SDK** credentials.

### What You Have (Web SDK - NOT NEEDED):
```javascript
// This is for frontend JavaScript apps
const firebaseConfig = {
  apiKey: "AIzaSyApOINpoCccJnU-cXHa6XT6fpaGp9qIp28",
  authDomain: "whatsapp-automation-a8d2d.firebaseapp.com",
  projectId: "whatsapp-automation-a8d2d",
  // ... etc
};
```

### What You Need (Admin SDK):
```json
{
  "type": "service_account",
  "project_id": "whatsapp-automation-a8d2d",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@whatsapp-automation-a8d2d.iam.gserviceaccount.com",
  // ... etc
}
```

---

## 📝 Step-by-Step: Get Admin SDK Credentials

### Step 1: Go to Firebase Console

Open this direct link:
```
https://console.firebase.google.com/project/whatsapp-automation-a8d2d/settings/serviceaccounts/adminsdk
```

Or manually:
1. Go to https://console.firebase.google.com/
2. Select your project: **whatsapp-automation-a8d2d**
3. Click the gear icon (⚙️) → **Project settings**
4. Click the **"Service accounts"** tab

### Step 2: Generate Private Key

1. You'll see a section called **"Firebase Admin SDK"**
2. Click the button **"Generate new private key"**
3. A popup will appear - click **"Generate key"**
4. A JSON file will download (e.g., `whatsapp-automation-a8d2d-xxxxx.json`)

### Step 3: Copy Values to .env File

Open the downloaded JSON file. It looks like:

```json
{
  "type": "service_account",
  "project_id": "whatsapp-automation-a8d2d",
  "private_key_id": "abc123def456...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQE...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@whatsapp-automation-a8d2d.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

Now edit your `.env` file:

```bash
nano .env
# OR
open -e .env
```

And fill in these three values from the JSON:

```env
FIREBASE_PROJECT_ID=whatsapp-automation-a8d2d

# Copy the ENTIRE private_key value (including \n characters)
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG...\n-----END PRIVATE KEY-----\n

# Copy the client_email value
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@whatsapp-automation-a8d2d.iam.gserviceaccount.com
```

### Step 4: Generate Flask Secret Key

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and use it as `FLASK_SECRET_KEY` in `.env`:

```env
FLASK_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

---

## ⚠️ Important Notes

### About the Private Key

The `private_key` field in the JSON has `\n` characters (two characters: backslash + n), **NOT actual line breaks**.

✅ **CORRECT** - Keep the \n as two characters:
```env
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvQIB...\n-----END PRIVATE KEY-----\n
```

❌ **WRONG** - Don't replace \n with actual line breaks:
```env
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
MIIEvQIB...
-----END PRIVATE KEY-----
```

### Security

- ⚠️ **Never commit** the `.env` file or the downloaded JSON to git
- ⚠️ **Never share** these credentials publicly
- ⚠️ The JSON file contains sensitive credentials - keep it secure
- ⚠️ Delete the JSON file after copying values to `.env`

---

## ✅ Verify Your Setup

### Check Firestore is Enabled

1. Go to: https://console.firebase.google.com/project/whatsapp-automation-a8d2d/firestore
2. You should see "Cloud Firestore" database
3. If not, click **"Create database"** and enable it

### Test Firebase Connection

Create a test file:

```bash
cat > test_firebase.py << 'EOF'
from firebase_service import FirebaseService

try:
    firebase = FirebaseService()
    print("✅ Firebase connected successfully!")
    print(f"✅ Database: {firebase.db}")
except Exception as e:
    print(f"❌ Firebase error: {e}")
    print("\nCheck your .env file configuration!")
EOF

python3 test_firebase.py
```

If successful, you'll see:
```
✅ Firebase connected successfully!
✅ Database: <google.cloud.firestore_v1.client.Client object at 0x...>
```

---

## 🚀 Your Complete .env File Should Look Like:

```env
# Flask Configuration
FLASK_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6

# Firebase Admin SDK Configuration
FIREBASE_PROJECT_ID=whatsapp-automation-a8d2d
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASC...your-full-key...\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-a1b2c3@whatsapp-automation-a8d2d.iam.gserviceaccount.com

# WhatsApp Automation Settings
MIN_DELAY_SECONDS=15
MAX_DELAY_SECONDS=30

# Server Configuration
PORT=5000
DEBUG=false
```

---

## 📋 Checklist

- [ ] Visited Firebase Console service accounts page
- [ ] Generated new private key
- [ ] Downloaded JSON file
- [ ] Copied `project_id` to `FIREBASE_PROJECT_ID`
- [ ] Copied `private_key` to `FIREBASE_PRIVATE_KEY` (with \n characters)
- [ ] Copied `client_email` to `FIREBASE_CLIENT_EMAIL`
- [ ] Generated and added `FLASK_SECRET_KEY`
- [ ] Verified Firestore is enabled
- [ ] Tested connection with test script
- [ ] Deleted the downloaded JSON file (after copying values)

---

## 🆘 Troubleshooting

### "Invalid service account credentials"
- Check that you copied the ENTIRE private_key value
- Ensure `\n` characters are preserved (not actual line breaks)
- Verify the client_email is correct

### "Permission denied"
- Make sure you downloaded the key from the correct Firebase project
- Check that Firestore is enabled in Firebase Console

### "Module not found"
- Make sure virtual environment is activated: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

---

## ✅ Next Steps

Once your `.env` file is configured:

1. **Start the application:**
   ```bash
   ./start.sh
   # OR
   python app.py
   ```

2. **Open the dashboard:**
   ```
   http://localhost:5000
   ```

3. **Follow GET_STARTED.md** for the rest of the setup!

---

**Need more help?** See:
- [GET_STARTED.md](GET_STARTED.md) - Complete setup guide
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick reference
