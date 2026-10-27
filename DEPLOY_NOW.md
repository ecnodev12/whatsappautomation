# 🚀 Quick Deploy to Google Cloud Run

## Step 1: Install gcloud CLI

```bash
# Open Terminal and run:
/opt/homebrew/bin/firebase --version

# If firebase works but gcloud doesn't, install gcloud:
brew install --cask google-cloud-sdk

# OR download from: https://cloud.google.com/sdk/docs/install
```

## Step 2: Initialize gcloud (One-time setup)

```bash
# Initialize and login
gcloud init

# When prompted:
# 1. Login with your Google account (the one with Firebase access)
# 2. Select project: whatsapp-automation-a8d2d
# 3. Select region: us-central1 (or your preferred region)
```

## Step 3: Deploy Your App

```bash
cd /Users/apple/Desktop/whatsappautomation
./deploy.sh
```

That's it! The script will:
1. ✅ Build your Docker container
2. ✅ Upload to Google Cloud
3. ✅ Deploy to Cloud Run
4. ✅ Give you a public URL

## 🌐 Your App Will Be Live At:

```
https://whatsapp-automation-XXXXX-uc.a.run.app
```

## ⚠️ Important: WhatsApp Sessions

Cloud Run containers restart frequently, which means WhatsApp sessions won't persist by default.

**Solutions:**
1. **Quick Fix**: Keep the container warm with uptime monitoring
2. **Better Fix**: Store sessions in Cloud Storage (requires code changes)
3. **Best Fix**: Use a dedicated VM if you need 24/7 sessions

For now, you'll need to re-scan the QR code after container restarts.

## 💰 Cost

- Free tier: First 2M requests/month FREE
- After that: ~$10-30/month for moderate use
- Billed per second of usage

## 🎯 Need Help?

If deployment fails, run:
```bash
gcloud builds log --region=us-central1
```

Or share the error and I'll help fix it!
