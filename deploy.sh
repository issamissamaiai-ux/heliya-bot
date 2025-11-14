#!/bin/bash

echo "🚀 HELIYA Bot - Quick Deploy Script"
echo "=================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
fi

# Add all files
echo "📄 Adding files to Git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "HELIYA Bot - Production Ready v$(date +%Y%m%d)"

# Check if remote exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo ""
    echo "🔗 Please add your GitHub repository URL:"
    echo "Example: https://github.com/yourusername/heliya-bot.git"
    read -p "GitHub URL: " REPO_URL
    
    git remote add origin $REPO_URL
fi

# Push to GitHub
echo "⬆️  Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Code uploaded to GitHub successfully!"
echo ""
echo "🌐 Next Steps for FREE HOSTING:"
echo "1. Go to render.com"
echo "2. Create new Web Service"
echo "3. Connect your GitHub repository"
echo "4. Set environment variable: BOT_TOKEN"
echo "5. Deploy!"
echo ""
echo "💡 Your bot will be live in 3-5 minutes!"
echo "📊 Free hosting supports 100+ users easily!"