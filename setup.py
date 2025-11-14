#!/usr/bin/env python3
"""
Setup script for Heliya Bot
This script helps with the initial setup and configuration
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 أو أحدث مطلوب!")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} مثبت")

def install_requirements():
    """Install required packages."""
    print("📦 جاري تثبيت المكتبات المطلوبة...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ تم تثبيت المكتبات بنجاح!")
    except subprocess.CalledProcessError:
        print("❌ فشل في تثبيت المكتبات!")
        sys.exit(1)

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
        print("✅ FFmpeg مثبت ومتاح")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  FFmpeg غير مثبت!")
        print("📋 تعليمات تثبيت FFmpeg:")
        
        if platform.system() == "Windows":
            print("   1. اذهب إلى https://ffmpeg.org/download.html")
            print("   2. حمل النسخة المناسبة لـ Windows")
            print("   3. استخرج الملف وأضف مجلد bin إلى PATH")
        elif platform.system() == "Darwin":  # macOS
            print("   قم بتشغيل: brew install ffmpeg")
        else:  # Linux
            print("   Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg")
            print("   CentOS/RHEL: sudo yum install ffmpeg")

def setup_config():
    """Help user setup configuration."""
    print("\n🔧 إعداد البوت:")
    
    config_file = "config.py"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'YOUR_BOT_TOKEN_HERE' in content:
            print("⚠️  يجب عليك تحديث BOT_TOKEN في config.py")
            print("📋 خطوات الحصول على Token:")
            print("   1. ابحث عن @BotFather في تلجرام")
            print("   2. أرسل /newbot")
            print("   3. اتبع التعليمات")
            print("   4. انسخ الـ Token واستبدله في config.py")
        else:
            print("✅ config.py يبدو معدّل بشكل صحيح")
    else:
        print("❌ ملف config.py غير موجود!")

def create_directories():
    """Create necessary directories."""
    directories = ['downloads', 'logs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ تم إنشاء مجلد {directory}")

def main():
    """Main setup function."""
    print("🎬 مرحباً بك في إعداد بوت HELIYA!")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install requirements
    install_requirements()
    
    # Check FFmpeg
    check_ffmpeg()
    
    # Setup config
    setup_config()
    
    print("\n" + "=" * 50)
    print("🎉 تم الإعداد بنجاح!")
    print("\n📋 الخطوات التالية:")
    print("1. تحديث BOT_TOKEN في config.py")
    print("2. تشغيل البوت: python bot.py")
    print("3. اختبار البوت في تلجرام")
    
    if platform.system() == "Windows":
        print("\n💡 نصيحة: يمكنك تشغيل start_bot.bat لبدء البوت بسهولة")

if __name__ == "__main__":
    main()