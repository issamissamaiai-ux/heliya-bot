#!/usr/bin/env python3
"""
HELIYA Bot - Production Version with Full Multilingual Support
بوت هيليا للإنتاج مع دعم كامل لأربع لغات

Optimized for free hosting platforms (Render, Railway, etc.)
مُحسن للاستضافة المجانية مع الحفاظ على جميع اللغات
"""

import os
import logging
import time
import threading
from urllib.parse import urlparse
from pathlib import Path
import telebot
from telebot import types

# Configure logging for production
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token - use environment variable for security in production
BOT_TOKEN = os.getenv('BOT_TOKEN', '8313839473:AAG7tABrAAWnCRoNh5AiQQyrumWR8_6O-vg')

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# User data storage (in production, use a database)
user_data = {}

# Complete multilingual messages - Full translations for production
MESSAGES = {
    'ar': {
        'welcome': """🎬 أهلاً وسهلاً {name}!

مرحباً بك في بوت HELIYA لتحميل الفيديوهات! 🚀

✨ أرسل لي أي رابط فيديو وسأحمله لك بدون علامة مائية!

📱 المنصات المدعومة:
• YouTube & YouTube Shorts 📺
• TikTok (بدون علامة مائية) 🎵
• Instagram (Posts & Reels) 📸
• Facebook & FB Watch 📘
• Twitter/X 🐦
• Reddit 🔴
• وأكثر من 1000+ منصة!

🎯 فقط أرسل الرابط وانتظر المفاجأة!""",
        
        'language_select': "🌍 اختر لغتك المفضلة:",
        'language_changed': "✅ تم تغيير اللغة إلى العربية بنجاح!",
        'help_button': "❓ دليل الاستخدام",
        'quality_button': "⚙️ إعدادات الجودة", 
        'language_button': "🌍 تغيير اللغة",
        'processing': "⏳ جاري معالجة الرابط...\n\n⏰ قد يستغرق حتى 30 ثانية",
        'analyzing': "🔍 جاري تحليل الرابط وفحص توفر الفيديو...",
        'extracting': "📊 جاري استخراج معلومات الفيديو...",
        'downloading': "⬇️ بدء التحميل الفعلي...",
        'uploading': "📤 جاري رفع الفيديو إلى تلجرام...",
        'success': "✅ تم التحميل بنجاح! 🎉\n\n💡 أرسل رابط آخر للمزيد من التحميلات!\n⚙️ استخدم /quality لتغيير الجودة",
        'invalid_url': "❌ لم أتمكن من فهم رسالتك. أرسل لي رابط فيديو للتحميل!",
        'file_too_large': "❌ حجم الفيديو ({size:.1f} ميجابايت) أكبر من 50 ميجابايت.\n\n💡 جرب:\n• فيديو أقصر\n• جودة أقل من /quality",
        'video_unavailable': "❌ الفيديو غير متاح:\n\n• قد يكون محذوف\n• حساب خاص\n• محمي بحقوق النشر\n\n💡 جرب رابط آخر",
        'quality_select': "🎥 اختر جودة التحميل المفضلة:\n\n💡 نصيحة: الجودة الأعلى = حجم أكبر = وقت أطول",
        'help_detailed': """📖 دليل الاستخدام المفصل:

🔗 كيفية الاستخدام:
1️⃣ انسخ رابط الفيديو من التطبيق
2️⃣ الصق الرابط هنا في الشات
3️⃣ انتظر لحظات (قد تستغرق 30 ثانية)
4️⃣ استقبل الفيديو بدون علامة مائية! 🎉

🎯 أوامر مفيدة:
• /start - صفحة البداية
• /help - هذا الدليل
• /quality - اختيار جودة التحميل

💡 نصائح مهمة:
✅ تأكد أن الرابط صحيح ومكتمل
✅ الفيديو يجب أن يكون متاح للجمهور
✅ أقصى حجم ملف: 50 ميجابايت"""
    },
    
    'en': {
        'welcome': """🎬 Welcome {name}!

Welcome to HELIYA Video Downloader Bot! 🚀

✨ Send me any video link and I'll download it without watermarks!

📱 Supported Platforms:
• YouTube & YouTube Shorts 📺
• TikTok (no watermark) 🎵
• Instagram (Posts & Reels) 📸
• Facebook & FB Watch 📘
• Twitter/X 🐦
• Reddit 🔴
• And 1000+ more platforms!

🎯 Just send the link and wait for magic!""",
        
        'language_select': "🌍 Choose your preferred language:",
        'language_changed': "✅ Language changed to English successfully!",
        'help_button': "❓ Help Guide",
        'quality_button': "⚙️ Quality Settings",
        'language_button': "🌍 Change Language", 
        'processing': "⏳ Processing link...\n\n⏰ May take up to 30 seconds",
        'analyzing': "🔍 Analyzing link and checking video availability...",
        'extracting': "📊 Extracting video information...",
        'downloading': "⬇️ Starting actual download...",
        'uploading': "📤 Uploading video to Telegram...",
        'success': "✅ Download successful! 🎉\n\n💡 Send another link for more downloads!\n⚙️ Use /quality to change quality",
        'invalid_url': "❌ I couldn't understand your message. Send me a video link to download!",
        'file_too_large': "❌ Video size ({size:.1f} MB) is larger than 50 MB.\n\n💡 Try:\n• Shorter video\n• Lower quality from /quality",
        'video_unavailable': "❌ Video unavailable:\n\n• May be deleted\n• Private account\n• Copyright protected\n\n💡 Try another link",
        'quality_select': "🎥 Choose your preferred download quality:\n\n💡 Tip: Higher quality = larger size = longer time",
        'help_detailed': """📖 Detailed Usage Guide:

🔗 How to use:
1️⃣ Copy video link from app
2️⃣ Paste link here in chat
3️⃣ Wait a moment (may take 30 seconds)
4️⃣ Receive video without watermark! 🎉

🎯 Useful commands:
• /start - Home page
• /help - This guide
• /quality - Choose download quality

💡 Important tips:
✅ Make sure link is correct and complete
✅ Video must be publicly available
✅ Maximum file size: 50 MB"""
    },
    
    'fa': {
        'welcome': """🎬 خوش آمدید {name}!

به ربات دانلود ویدیو HELIYA خوش آمدید! 🚀

✨ هر لینک ویدیویی بفرستید و بدون واترمارک دانلود می‌کنم!

📱 پلتفرم‌های پشتیبانی شده:
• YouTube & YouTube Shorts 📺
• TikTok (بدون واترمارک) 🎵
• Instagram (پست‌ها و ریل‌ها) 📸
• Facebook & FB Watch 📘
• Twitter/X 🐦
• Reddit 🔴
• و بیش از 1000 پلتفرم دیگر!

🎯 فقط لینک را بفرستید و منتظر معجزه باشید!""",
        
        'language_select': "🌍 زبان مورد نظر خود را انتخاب کنید:",
        'language_changed': "✅ زبان با موفقیت به فارسی تغییر کرد!",
        'help_button': "❓ راهنمای استفاده",
        'quality_button': "⚙️ تنظیمات کیفیت",
        'language_button': "🌍 تغییر زبان",
        'processing': "⏳ در حال پردازش لینک...\n\n⏰ ممکن است تا 30 ثانیه طول بکشد",
        'analyzing': "🔍 در حال تجزیه و تحلیل لینک و بررسی دسترسی ویدیو...",
        'extracting': "📊 در حال استخراج اطلاعات ویدیو...",
        'downloading': "⬇️ شروع دانلود واقعی...",
        'uploading': "📤 در حال آپلود ویدیو به تلگرام...",
        'success': "✅ دانلود موفقیت‌آمیز بود! 🎉\n\n💡 لینک دیگری برای دانلود بیشتر بفرستید!\n⚙️ از /quality برای تغییر کیفیت استفاده کنید",
        'invalid_url': "❌ نتوانستم پیام شما را درک کنم. لینک ویدیو برای دانلود بفرستید!",
        'file_too_large': "❌ حجم ویدیو ({size:.1f} مگابایت) بیشتر از 50 مگابایت است.\n\n💡 امتحان کنید:\n• ویدیوی کوتاه‌تر\n• کیفیت پایین‌تر از /quality",
        'video_unavailable': "❌ ویدیو در دسترس نیست:\n\n• ممکن است حذف شده باشد\n• اکانت خصوصی\n• محافظت شده با کپی رایت\n\n💡 لینک دیگری امتحان کنید",
        'quality_select': "🎥 کیفیت دانلود مورد نظر خود را انتخاب کنید:\n\n💡 نکته: کیفیت بالاتر = حجم بیشتر = زمان بیشتر",
        'help_detailed': """📖 راهنمای کامل استفاده:

🔗 نحوه استفاده:
1️⃣ لینک ویدیو را از اپ کپی کنید
2️⃣ لینک را اینجا در چت پیست کنید
3️⃣ لحظه‌ای صبر کنید (ممکن است 30 ثانیه طول بکشد)
4️⃣ ویدیو را بدون واترمارک دریافت کنید! 🎉

🎯 دستورات مفید:
• /start - صفحه اصلی
• /help - این راهنما
• /quality - انتخاب کیفیت دانلود

💡 نکات مهم:
✅ مطمئن شوید لینک صحیح و کامل است
✅ ویدیو باید برای عموم در دسترس باشد
✅ حداکثر حجم فایل: 50 مگابایت"""
    },
    
    'fr': {
        'welcome': """🎬 Bienvenue {name}!

Bienvenue sur le bot de téléchargement vidéo HELIYA! 🚀

✨ Envoyez-moi n'importe quel lien vidéo et je le téléchargerai sans filigrane!

📱 Plateformes supportées:
• YouTube & YouTube Shorts 📺
• TikTok (sans filigrane) 🎵
• Instagram (Posts & Reels) 📸
• Facebook & FB Watch 📘
• Twitter/X 🐦
• Reddit 🔴
• Et plus de 1000 plateformes!

🎯 Envoyez simplement le lien et attendez la magie!""",
        
        'language_select': "🌍 Choisissez votre langue préférée:",
        'language_changed': "✅ Langue changée en français avec succès!",
        'help_button': "❓ Guide d'aide",
        'quality_button': "⚙️ Paramètres de qualité",
        'language_button': "🌍 Changer la langue",
        'processing': "⏳ Traitement du lien...\n\n⏰ Peut prendre jusqu'à 30 secondes",
        'analyzing': "🔍 Analyse du lien et vérification de la disponibilité de la vidéo...",
        'extracting': "📊 Extraction des informations vidéo...",
        'downloading': "⬇️ Début du téléchargement réel...",
        'uploading': "📤 Téléchargement de la vidéo vers Telegram...",
        'success': "✅ Téléchargement réussi! 🎉\n\n💡 Envoyez un autre lien pour plus de téléchargements!\n⚙️ Utilisez /quality pour changer la qualité",
        'invalid_url': "❌ Je n'ai pas pu comprendre votre message. Envoyez-moi un lien vidéo à télécharger!",
        'file_too_large': "❌ La taille de la vidéo ({size:.1f} MB) est supérieure à 50 MB.\n\n💡 Essayez:\n• Vidéo plus courte\n• Qualité inférieure avec /quality",
        'video_unavailable': "❌ Vidéo non disponible:\n\n• Peut être supprimée\n• Compte privé\n• Protégé par le droit d'auteur\n\n💡 Essayez un autre lien",
        'quality_select': "🎥 Choisissez votre qualité de téléchargement préférée:\n\n💡 Conseil: Qualité supérieure = taille plus grande = temps plus long",
        'help_detailed': """📖 Guide d'utilisation détaillé:

🔗 Comment utiliser:
1️⃣ Copiez le lien vidéo depuis l'app
2️⃣ Collez le lien ici dans le chat
3️⃣ Attendez un moment (peut prendre 30 secondes)
4️⃣ Recevez la vidéo sans filigrane! 🎉

🎯 Commandes utiles:
• /start - Page d'accueil
• /help - Ce guide
• /quality - Choisir la qualité de téléchargement

💡 Conseils importants:
✅ Assurez-vous que le lien est correct et complet
✅ La vidéo doit être publiquement disponible
✅ Taille maximale du fichier: 50 MB"""
    }
}

def get_user_language(user_id):
    """Get user's preferred language, default to Arabic"""
    return user_data.get(user_id, {}).get('language', 'ar')

def get_message(user_id, key, **kwargs):
    """Get localized message for user"""
    lang = get_user_language(user_id)
    message = MESSAGES[lang].get(key, MESSAGES['ar'][key])
    return message.format(**kwargs) if kwargs else message

@bot.message_handler(commands=['start'])
def start_command(message):
    """Handle /start command with language selection"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Friend"
    
    # Check if user has selected a language
    if user_id not in user_data or 'language' not in user_data[user_id]:
        # Show language selection
        markup = types.InlineKeyboardMarkup()
        
        ar_btn = types.InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")
        en_btn = types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")
        fa_btn = types.InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa")
        fr_btn = types.InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")
        
        markup.row(ar_btn, en_btn)
        markup.row(fa_btn, fr_btn)
        
        bot.send_message(
            message.chat.id, 
            "🌍 Welcome! Please choose your language:\n"
            "🌍 أهلاً! اختر لغتك:\n"
            "🌍 خوش آمدید! زبان خود را انتخاب کنید:\n"
            "🌍 Bienvenue! Choisissez votre langue:",
            reply_markup=markup
        )
    else:
        # Show main welcome message
        show_welcome_message(message.chat.id, user_name, user_id)

def show_welcome_message(chat_id, user_name, user_id):
    """Show welcome message in user's selected language"""
    welcome_text = get_message(user_id, 'welcome', name=user_name)
    
    markup = types.InlineKeyboardMarkup()
    help_btn = types.InlineKeyboardButton(
        get_message(user_id, 'help_button'), 
        callback_data="help"
    )
    quality_btn = types.InlineKeyboardButton(
        get_message(user_id, 'quality_button'), 
        callback_data="quality"
    )
    lang_btn = types.InlineKeyboardButton(
        get_message(user_id, 'language_button'), 
        callback_data="language"
    )
    
    markup.row(help_btn)
    markup.row(quality_btn)
    markup.row(lang_btn)
    
    bot.send_message(chat_id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Handle button callbacks - Fixed multilingual version"""
    user_id = call.from_user.id
    user_name = call.from_user.first_name or "Friend"
    
    try:
        if call.data.startswith("lang_"):
            # Language selection - FIXED VERSION
            lang = call.data.split("_")[1]
            
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['language'] = lang
            
            # Show language changed message in the NEW language
            bot.edit_message_text(
                get_message(user_id, 'language_changed'),
                call.message.chat.id, 
                call.message.message_id
            )
            
            # Show welcome message in new language after short delay
            time.sleep(1)
            show_welcome_message(call.message.chat.id, user_name, user_id)
            
        elif call.data == "language":
            # Show language selection menu
            markup = types.InlineKeyboardMarkup()
            
            ar_btn = types.InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")
            en_btn = types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")
            fa_btn = types.InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa")
            fr_btn = types.InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")
            
            markup.row(ar_btn, en_btn)
            markup.row(fa_btn, fr_btn)
            
            bot.edit_message_text(
                get_message(user_id, 'language_select'),
                call.message.chat.id, 
                call.message.message_id,
                reply_markup=markup
            )
            
        elif call.data == "help":
            help_text = get_message(user_id, 'help_detailed')
            bot.edit_message_text(
                help_text, 
                call.message.chat.id, 
                call.message.message_id
            )
            
        elif call.data == "quality":
            markup = types.InlineKeyboardMarkup()
            
            btn1 = types.InlineKeyboardButton("🎬 1080p Full HD", callback_data="quality_1080")
            btn2 = types.InlineKeyboardButton("📺 720p HD", callback_data="quality_720")
            btn3 = types.InlineKeyboardButton("📱 480p Mobile", callback_data="quality_480")
            btn4 = types.InlineKeyboardButton("⚡ 360p Fast", callback_data="quality_360")
            btn5 = types.InlineKeyboardButton("🌟 Best Available", callback_data="quality_best")
            
            markup.row(btn1, btn2)
            markup.row(btn3, btn4)
            markup.row(btn5)
            
            bot.edit_message_text(
                get_message(user_id, 'quality_select'),
                call.message.chat.id, 
                call.message.message_id,
                reply_markup=markup
            )
            
        elif call.data.startswith("quality_"):
            quality = call.data.split("_")[1]
            
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['preferred_quality'] = quality
            
            quality_names = {
                '360': '⚡ 360p Fast',
                '480': '📱 480p Mobile', 
                '720': '📺 720p HD',
                '1080': '🎬 1080p Full HD',
                'best': '🌟 Best Available'
            }
            
            # Create success message based on language
            lang = get_user_language(user_id)
            if lang == 'ar':
                success_text = f"✅ تم حفظ الإعدادات!\n\n🎯 الجودة المختارة: {quality_names.get(quality, quality)}\n\n🔗 الآن أرسل رابط الفيديو للبدء!"
            elif lang == 'fa':
                success_text = f"✅ تنظیمات ذخیره شد!\n\n🎯 کیفیت انتخاب شده: {quality_names.get(quality, quality)}\n\n🔗 حالا لینک ویدیو را برای شروع بفرستید!"
            elif lang == 'fr':
                success_text = f"✅ Paramètres sauvegardés!\n\n🎯 Qualité sélectionnée: {quality_names.get(quality, quality)}\n\n🔗 Maintenant envoyez le lien vidéo pour commencer!"
            else:  # English
                success_text = f"✅ Settings saved!\n\n🎯 Selected quality: {quality_names.get(quality, quality)}\n\n🔗 Now send video link to start!"
            
            bot.edit_message_text(
                success_text,
                call.message.chat.id, 
                call.message.message_id
            )
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Callback handler error: {e}")
        bot.answer_callback_query(call.id, "حدث خطأ / Error occurred")

def is_video_url(url):
    """Check if URL contains video platforms"""
    video_domains = [
        'youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com', 
        'facebook.com', 'fb.watch', 'twitter.com', 'x.com', 
        'reddit.com', 'twitch.tv', 'vimeo.com', 'dailymotion.com'
    ]
    return any(domain in url.lower() for domain in video_domains)

def is_valid_url(url):
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def process_video_url(message):
    """Process video URL - optimized for hosting"""
    try:
        import yt_dlp
    except ImportError:
        bot.send_message(message.chat.id, "❌ Video processing temporarily unavailable. Please try again later.")
        return
    
    url = message.text.strip()
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Friend"
    
    processing_msg = bot.send_message(
        message.chat.id, 
        f"🎬 {user_name}!\n\n" + get_message(user_id, 'processing')
    )
    
    try:
        # Get user preferences
        preferred_quality = user_data.get(user_id, {}).get('preferred_quality', 'best')
        
        # Update status
        bot.edit_message_text(
            get_message(user_id, 'analyzing'), 
            message.chat.id, 
            processing_msg.message_id
        )
        
        # Create downloads directory
        downloads_dir = Path("downloads")
        downloads_dir.mkdir(exist_ok=True)
        
        # Configure yt-dlp options (optimized for hosting)
        format_selector = 'best[ext=mp4][filesize<50M]/best[filesize<50M]/best'
        if preferred_quality != 'best' and preferred_quality.isdigit():
            format_selector = f'best[height<={preferred_quality}][ext=mp4][filesize<50M]/best[filesize<50M]'
            
        ydl_opts = {
            'format': format_selector,
            'outtmpl': str(downloads_dir / '%(title).50s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 20,
            'retries': 2,
            'fragment_retries': 2,
        }
        
        # Extract and download
        bot.edit_message_text(
            get_message(user_id, 'extracting'), 
            message.chat.id, 
            processing_msg.message_id
        )
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                title = (info.get('title') or 'Video')[:30]
                
                # Check file size
                filesize = info.get('filesize') or info.get('filesize_approx')
                if filesize and filesize > 50 * 1024 * 1024:
                    bot.edit_message_text(
                        get_message(user_id, 'file_too_large', size=filesize/(1024*1024)),
                        message.chat.id, 
                        processing_msg.message_id
                    )
                    return
                
                bot.edit_message_text(
                    get_message(user_id, 'downloading'),
                    message.chat.id, 
                    processing_msg.message_id
                )
                
                # Download
                ydl.download([url])
                
                # Find downloaded file
                filename = ydl.prepare_filename(info)
                if not os.path.exists(filename):
                    base = os.path.splitext(filename)[0]
                    for ext in ['.mp4', '.webm', '.mkv']:
                        potential_file = base + ext
                        if os.path.exists(potential_file):
                            filename = potential_file
                            break
                
                if os.path.exists(filename) and os.path.getsize(filename) > 0:
                    bot.edit_message_text(
                        get_message(user_id, 'uploading'), 
                        message.chat.id, 
                        processing_msg.message_id
                    )
                    
                    # Send video
                    with open(filename, 'rb') as video_file:
                        bot.send_video(
                            message.chat.id,
                            video_file,
                            caption=f"🎬 {title}\n\n📥 Downloaded by HELIYA Bot",
                            supports_streaming=True,
                            timeout=60
                        )
                    
                    bot.send_message(message.chat.id, get_message(user_id, 'success'))
                    
                    # Cleanup
                    try:
                        bot.delete_message(message.chat.id, processing_msg.message_id)
                        os.remove(filename)
                    except:
                        pass
                        
                else:
                    bot.edit_message_text(
                        get_message(user_id, 'video_unavailable'),
                        message.chat.id, 
                        processing_msg.message_id
                    )
                    
            except Exception as e:
                logger.error(f"Download error: {e}")
                bot.edit_message_text(
                    get_message(user_id, 'video_unavailable'),
                    message.chat.id, 
                    processing_msg.message_id
                )
                    
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        bot.edit_message_text(
            get_message(user_id, 'video_unavailable'),
            message.chat.id, 
            processing_msg.message_id
        )

@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Handle text messages"""
    text = message.text
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Friend"
    
    # Check if user has selected language
    if user_id not in user_data or 'language' not in user_data[user_id]:
        start_command(message)
        return
    
    # Check if it's a video URL
    if is_video_url(text) or (is_valid_url(text) and text.startswith('http')):
        thread = threading.Thread(target=process_video_url, args=(message,))
        thread.daemon = True
        thread.start()
    else:
        # Invalid message response
        bot.send_message(
            message.chat.id,
            f"🤔 {user_name}!\n\n" + get_message(user_id, 'invalid_url')
        )

def main():
    """Run the multilingual production bot"""
    print("🎬 Starting HELIYA Bot - Production Version with 4 Languages...")
    print("� Languages: العربية | English | فارسی | Français")
    print("🚀 Optimized for free hosting (Render, Railway)...")
    print("✅ Bot ready for 100+ users with full multilingual support!")
    
    logger.info("🚀 Multilingual Production Heliya Bot starting...")
    
    try:
        # Use polling - works on all free hosting platforms
        bot.infinity_polling(
            timeout=30, 
            long_polling_timeout=10, 
            none_stop=True,
            interval=1,
            allowed_updates=None
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped successfully!")
        logger.info("Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        logger.error(f"Bot error: {e}")
        time.sleep(5)
        # Auto-restart on error for production stability
        main()

if __name__ == '__main__':
    main()