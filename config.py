#!/usr/bin/env python3
"""
Configuration file for Heliya Bot
"""

import os
from typing import List

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8313839473:AAG7tABrAAWnCRoNh5AiQQyrumWR8_6O-vg')

# Admin user IDs (replace with actual Telegram user IDs)
ADMIN_IDS: List[int] = [
    # Add your Telegram user ID here
    # Example: 123456789,
]

# Download Settings
MAX_FILE_SIZE_MB = 50  # Maximum file size in MB that can be sent via Telegram
DEFAULT_QUALITY = 'best'  # Default download quality
CLEANUP_INTERVAL_HOURS = 1  # How often to clean up downloaded files

# Supported file formats
SUPPORTED_FORMATS = ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm']

# Rate limiting (downloads per user per hour)
RATE_LIMIT_PER_USER = 10

# Download directory
DOWNLOADS_DIR = 'downloads'

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Bot messages in Arabic
MESSAGES = {
    'start': """
🎬 مرحبا بك في بوت تحميل الفيديوهات HELIYA!

أرسل لي رابط فيديو من أي منصة وسأقوم بتحميله بدون علامة مائية!

المنصات المدعومة:
• YouTube
• TikTok  
• Instagram
• Facebook
• Twitter/X
• Reddit
• وأكثر من 1000+ منصة أخرى!

فقط أرسل الرابط وسأقوم بالباقي! 🚀
    """,
    
    'help': """
🔧 كيفية استخدام البوت:

1️⃣ انسخ رابط الفيديو من أي منصة
2️⃣ أرسل الرابط في الشات
3️⃣ انتظر قليلاً بينما أقوم بالتحميل
4️⃣ احصل على الفيديو بدون علامة مائية!

📝 أوامر البوت:
/start - بدء استخدام البوت
/help - عرض هذه الرسالة
/quality - اختيار جودة التحميل

⚠️ ملاحظات مهمة:
• حد أقصى لحجم الملف: {max_size} MB
• يدعم معظم المنصات الشهيرة
• التحميل مجاني تماماً

🆘 إذا واجهت مشكلة، تأكد من:
• صحة الرابط
• أن الفيديو متاح للعامة
• أن حجم الفيديو ليس كبيراً جداً
    """,
    
    'processing': '⏳ جاري معالجة الرابط...',
    'extracting_info': '🔍 جاري استخراج معلومات الفيديو...',
    'downloading': '⬇️ جاري التحميل...',
    'uploading': '📤 جاري رفع الفيديو...',
    
    'error_invalid_url': '❌ الرابط غير صحيح! تأكد من أنك أرسلت رابط فيديو صالح.',
    'error_file_too_large': '❌ حجم الفيديو ({size:.1f} MB) أكبر من الحد المسموح ({max_size} MB).',
    'error_download_failed': '❌ فشل في تحميل الفيديو. حاول مرة أخرى.',
    'error_generic': '❌ حدث خطأ أثناء تحميل الفيديو. حاول مرة أخرى لاحقاً.',
    'error_not_accessible': '❌ لا يمكن الوصول للفيديو. تأكد من أن الرابط صحيح والفيديو متاح.',
    
    'unknown_message': """
🤔 لم أفهم الرسالة.

أرسل لي رابط فيديو للتحميل، أو استخدم /help للمساعدة.
    """,
    
    'video_caption': '🎬 {title}\n\n📥 تم التحميل بواسطة @HeliyaBot'
}

# Quality options
QUALITY_OPTIONS = {
    'best': 'أفضل جودة متاحة',
    '1080': 'Full HD (1080p)', 
    '720': 'HD (720p)',
    '480': 'موبايل (480p)',
    '360': 'سريع (360p)'
}