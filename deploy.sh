#!/bin/bash

# WhatsApp Automation - Deploy to Google Cloud Run
# This script deploys your Flask app to Cloud Run (serverless containers)

set -e

echo "🚀 Deploying WhatsApp Automation to Google Cloud Run..."

# Configuration
PROJECT_ID="whatsapp-automation-a8d2d"
SERVICE_NAME="whatsapp-automation"
REGION="us-central1"  # Change if needed
PLATFORM="managed"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed.${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo -e "${BLUE}📦 Setting project to: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs (if not already enabled)
echo -e "${BLUE}🔧 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Read environment variables from .env
echo -e "${BLUE}📋 Reading environment variables from .env${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi

# Extract Firebase credentials from .env
FIREBASE_PROJECT_ID=$(grep FIREBASE_PROJECT_ID .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
FIREBASE_PRIVATE_KEY=$(grep FIREBASE_PRIVATE_KEY .env | cut -d '=' -f2-)
FIREBASE_CLIENT_EMAIL=$(grep FIREBASE_CLIENT_EMAIL .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")

# Build and deploy to Cloud Run
echo -e "${BLUE}🏗️  Building and deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform $PLATFORM \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 1 \
    --set-env-vars "FIREBASE_PROJECT_ID=$FIREBASE_PROJECT_ID" \
    --set-env-vars "FIREBASE_CLIENT_EMAIL=$FIREBASE_CLIENT_EMAIL" \
    --set-env-vars "FIREBASE_PRIVATE_KEY=$FIREBASE_PRIVATE_KEY" \
    --set-env-vars "PORT=8080" \
    --set-env-vars "DEFAULT_COUNTRY_CODE=91"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform $PLATFORM --region $REGION --format 'value(status.url)')

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}🌐 Your app is live at:${NC} ${BLUE}$SERVICE_URL${NC}"
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo "1. Visit your app: $SERVICE_URL"
echo "2. Connect WhatsApp Web browser"
echo "3. Start your campaigns!"
echo ""
echo -e "${BLUE}💡 Useful commands:${NC}"
echo "  - View logs: gcloud run logs read --service=$SERVICE_NAME --region=$REGION"
echo "  - Update: ./deploy.sh"
echo "  - Delete: gcloud run services delete $SERVICE_NAME --region=$REGION"
