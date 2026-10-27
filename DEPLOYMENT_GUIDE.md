# 🚀 Deployment Guide - WhatsApp Automation

This guide will help you deploy your WhatsApp automation dashboard to Google Cloud Run (serverless).

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
3. **Firebase Project** (you already have: `whatsapp-automation-a8d2d`)

## 🔧 One-Time Setup

### 1. Install gcloud CLI (if not installed)

```bash
# macOS
brew install --cask google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### 2. Initialize gcloud

```bash
gcloud init
# Select your Google account
# Select project: whatsapp-automation-a8d2d
# Select region: us-central1 (or your preferred region)
```

### 3. Authenticate

```bash
gcloud auth login
gcloud auth application-default login
```

## 🚀 Deploy to Cloud Run

### Option 1: Quick Deploy (Recommended)

```bash
cd /Users/apple/Desktop/whatsappautomation
./deploy.sh
```

This script will:
- ✅ Enable required Google Cloud APIs
- ✅ Build Docker container from your code
- ✅ Deploy to Cloud Run
- ✅ Set environment variables from .env
- ✅ Give you a public URL

### Option 2: Manual Deploy

```bash
cd /Users/apple/Desktop/whatsappautomation

# Set your project
gcloud config set project whatsapp-automation-a8d2d

# Enable APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# Deploy
gcloud run deploy whatsapp-automation \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 1
```

## 🌐 After Deployment

Your app will be available at a URL like:
```
https://whatsapp-automation-XXXXX-uc.a.run.app
```

**Important Notes:**

1. **WhatsApp Session Persistence**: Cloud Run is stateless - WhatsApp sessions may not persist between container restarts. For production, consider:
   - Using Cloud Storage to store session data
   - Implementing session backup/restore
   - Using a dedicated VM if sessions must persist

2. **Chromium in Cloud Run**: The Dockerfile includes all dependencies for Playwright/Chromium to work in Cloud Run

3. **Cold Starts**: First request after inactivity may take 20-30 seconds as the container starts

## 📊 Managing Your Deployment

### View Logs
```bash
gcloud run logs read --service=whatsapp-automation --region=us-central1 --limit=100
```

### Update Deployment
Just run the deploy script again:
```bash
./deploy.sh
```

### Update Environment Variables
```bash
gcloud run services update whatsapp-automation \
  --region=us-central1 \
  --set-env-vars "NEW_VAR=value"
```

### Scale Settings
```bash
# Set min/max instances
gcloud run services update whatsapp-automation \
  --region=us-central1 \
  --min-instances=0 \
  --max-instances=1
```

### Delete Service
```bash
gcloud run services delete whatsapp-automation --region=us-central1
```

## 💰 Cost Estimate

Cloud Run Pricing (pay per use):
- **Free tier**: 2 million requests/month, 360,000 GB-seconds/month
- **Your config**: 2GB RAM, 2 CPU, 1 max instance
- **Estimated cost**: $10-30/month for moderate use

[Cloud Run Pricing Calculator](https://cloud.google.com/products/calculator)

## 🔒 Security Notes

1. **Environment Variables**: Stored securely in Cloud Run
2. **Firebase Credentials**: Passed as environment variables (not in code)
3. **Authentication**: Currently allows unauthenticated access - add auth if needed
4. **HTTPS**: Automatic SSL/TLS certificate from Google

## 🐛 Troubleshooting

### Deployment fails
```bash
# Check build logs
gcloud builds log --region=us-central1

# Check service status
gcloud run services describe whatsapp-automation --region=us-central1
```

### Container crashes
```bash
# View error logs
gcloud run logs read --service=whatsapp-automation --region=us-central1 --limit=50
```

### Chromium issues
- Dockerfile includes all Chromium dependencies
- If issues persist, check Cloud Run logs for specific errors

## 📚 Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference/run)
- [Playwright in Docker](https://playwright.dev/docs/docker)

## 🎯 Alternative: Firebase Hosting + Cloud Functions

If you prefer Firebase Hosting (for the frontend) + Cloud Functions (for backend), let me know and I can set that up instead. However, Cloud Run is better for this use case because:
- ✅ Long-running WhatsApp sessions
- ✅ Browser automation support
- ✅ More memory and CPU control
- ✅ Easier deployment of full Flask app
