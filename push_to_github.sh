#!/bin/bash

# GitHub Push Script with Personal Access Token
# Usage: ./push_to_github.sh YOUR_GITHUB_TOKEN

if [ -z "$1" ]; then
    echo "❌ Error: GitHub token required"
    echo "Usage: ./push_to_github.sh YOUR_GITHUB_TOKEN"
    echo ""
    echo "Get your token from: https://github.com/settings/tokens"
    exit 1
fi

TOKEN=$1
REPO_URL="https://$TOKEN@github.com/ecnodev12/whatsappautomation.git"

echo "🔄 Updating remote URL with token..."
cd /Users/apple/Desktop/whatsappautomation
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

echo "📤 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo "🌐 View at: https://github.com/ecnodev12/whatsappautomation"
else
    echo "❌ Push failed. Check your token and permissions."
fi
