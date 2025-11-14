@echo off
echo 🚀 HELIYA Bot - Quick Deploy Script for Windows
echo ================================================

REM Check if git is initialized
if not exist ".git" (
    echo 📁 Initializing Git repository...
    git init
)

REM Add all files
echo 📄 Adding files to Git...
git add .

REM Commit changes
echo 💾 Committing changes...
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set mydate=%%c%%a%%b
git commit -m "HELIYA Bot - Production Ready v%mydate%"

REM Check if remote exists
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo.
    echo 🔗 Please add your GitHub repository URL:
    echo Example: https://github.com/yourusername/heliya-bot.git
    set /p REPO_URL="GitHub URL: "
    
    git remote add origin %REPO_URL%
)

REM Push to GitHub
echo ⬆️  Pushing to GitHub...
git push -u origin main

echo.
echo ✅ Code uploaded to GitHub successfully!
echo.
echo 🌐 Next Steps for FREE HOSTING:
echo 1. Go to render.com
echo 2. Create new Web Service
echo 3. Connect your GitHub repository
echo 4. Set environment variable: BOT_TOKEN = 8313839473:AAG7tABrAAWnCRoNh5AiQQyrumWR8_6O-vg
echo 5. Deploy!
echo.
echo 💡 Your bot will be live in 3-5 minutes!
echo 📊 Free hosting supports 100+ users easily!
echo.
pause