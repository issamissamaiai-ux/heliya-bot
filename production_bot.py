#!/usr/bin/env python3
"""
ISSAM Enhanced Test Bot - Webhook + Flask (Render)
"""

import os
import sys
import time
import logging
from pathlib import Path

from flask import Flask, request, abort
import telebot
import yt_dlp

# =========================
# Config
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN env variable is required")

PORT = int(os.environ.get("PORT", 5000))
BASE_URL = os.getenv("BASE_URL", "https://heliya-bot-1.onrender.com")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = BASE_URL.rstrip("/") + WEBHOOK_PATH

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
app = Flask(__name__)

# =========================
# Logging
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ISSAM_ENHANCED_WEBHOOK")
logger.info("PRODUCTION_BOT_STARTED")

# =========================
# Messages (Copie du code local)
# =========================

MESSAGES = {
    "ar": {
        "welcome": "🎬 مرحباً بك في بوت ISSAM المحسن للاختبار!\n\n💫 أرسل لي رابط فيديو من أي منصة وسأقوم بتحميله لك بدون علامة مائية!\n\nالمنصات المدعومة:\n• YouTube 📺\n• TikTok 🎵\n• Instagram 📸\n• Facebook 📘\n• Twitter 🐦\n• Reddit 📖\n• LinkedIn 💼\n• و أكثر من 1000 منصة أخرى!\n\n🎯 الجودة الافتراضية: 1080p فائقة\n\nاختر لغتك:",
        "choose_language": "🌍 اختر لغتك / Choose Language:",
        "language_set": "✅ تم تعيين اللغة العربية!",
        "send_link": "📎 أرسل رابط الفيديو الذي تريد تحميله:",
        "processing": "⏳ جاري معالجة الرابط...",
        "downloading": "⬇️ جاري تحميل الفيديو...",
        "uploading": "⬆️ جاري رفع الفيديو...",
        "success": "✅ تم التحميل بنجاح!",
        "error": "❌ حدث خطأ أثناء التحميل. يرجى المحاولة مرة أخرى.",
        "invalid_url": "❌ رابط غير صحيح. يرجى إرسال رابط صحيح.",
        "too_large": "❌ حجم الفيديو كبير جداً (أكثر من 50 ميجا). جرب فيديو أصغر.",
        "unsupported": "❌ منصة غير مدعومة أو فيديو غير متاح.",
        "back_to_menu": "🔙 العودة للقائمة الرئيسية",
        "help": "🆘 مساعدة",
        "help_text": "📚 كيفية استخدام البوت:\n\n1️⃣ أرسل رابط الفيديو\n2️⃣ انتظر التحميل\n3️⃣ احصل على الفيديو!\n\n💡 نصائح:\n• تأكد من أن الرابط صحيح\n• الفيديوهات الكبيرة تحتاج وقت أطول\n• بعض المنصات قد تتطلب تسجيل دخول\n\n🎯 البوت المحسن يدعم:\n• جودة عالية HD\n• تحميل سريع\n• معالجة أخطاء متقدمة\n• حماية من التضارب",
        "instagram_auth_error": "❌ فيديو الإنستغرام يتطلب تسجيل دخول\n\n📱 حاول استخدام منصات أخرى:\n• TikTok ✅\n• YouTube ✅\n• Facebook ✅\n• Twitter ✅\n• Reddit ✅\n\nأو جرب رابط إنستغرام آخر قد يكون عام.",
        "network_error": "❌ مشكلة في الاتصال بالإنترنت\n\n🔄 يرجى:\n• التأكد من اتصال الإنترنت\n• المحاولة مرة أخرى بعد قليل\n• التحقق من أن الرابط يعمل في المتصفح",
        "video_unavailable": "❌ الفيديو غير متاح حالياً\n\n💡 الأسباب المحتملة:\n• الفيديو محذوف أو خاص\n• مشكلة مؤقتة في المنصة\n• الرابط قديم أو منتهي الصلاحية\n\n🔄 جرب رابط آخر أو عد لاحقاً",
        "quality_info": "🎥 معلومات الجودة:",
        "processing_advanced": "🚀 معالجة متقدمة جارية...",
        "about": "ℹ️ حول البوت",
        "about_text": "🎬 بوت ISSAM المحسن للاختبار\n\n🔥 الميزات:\n• تحميل من 1000+ منصة\n• 4 لغات مدعومة\n• معالجة أخطاء متقدمة\n• حماية من التضارب\n• جودة عالية HD\n• تحميل سريع\n• اختيار الجودة المرغوبة\n\n👨‍💻 المطور: ISSAM\n🧪 إصدار الاختبار: v2.0\n📅 آخر تحديث: نوفمبر 2025",
        "quality_select": "🎥 اختر جودة الفيديو:",
        "quality_ultra": "💎 جودة فائقة (1080p)",
        "quality_hd": "🔥 جودة عالية HD (720p)",
        "quality_standard": "📺 جودة عادية (480p)",
        "quality_low": "📱 جودة منخفضة (360p)",
        "quality_audio": "🎵 صوت عالي الجودة (320kbps MP3)",
        "quality_selected": "تم اختيار الجودة:",
        "processing_quality": "⚙️ معالجة بالجودة المحددة...",
    },
    "en": {
        "welcome": "🎬 Welcome to ISSAM Enhanced Test Bot!\n\n💫 Send me a video link from any platform and I'll download it without watermark!\n\nSupported Platforms:\n• YouTube 📺\n• TikTok 🎵\n• Instagram 📸\n• Facebook 📘\n• Twitter 🐦\n• Reddit 📖\n• LinkedIn 💼\n• And 1000+ other platforms!\n\n🎯 Default Quality: Ultra 1080p\n\nChoose your language:",
        "choose_language": "🌍 اختر لغتك / Choose Language:",
        "language_set": "✅ English language has been set!",
        "send_link": "📎 Send the video link you want to download:",
        "processing": "⏳ Processing the link...",
        "downloading": "⬇️ Downloading video...",
        "uploading": "⬆️ Uploading video...",
        "success": "✅ Downloaded successfully!",
        "error": "❌ An error occurred during download. Please try again.",
        "invalid_url": "❌ Invalid link. Please send a valid link.",
        "too_large": "❌ Video file is too large (over 50MB). Try a smaller video.",
        "unsupported": "❌ Unsupported platform or video not available.",
        "back_to_menu": "🔙 Back to Main Menu",
        "help": "🆘 Help",
        "help_text": "📚 How to use the bot:\n\n1️⃣ Send video link\n2️⃣ Wait for download\n3️⃣ Get your video!\n\n💡 Tips:\n• Make sure the link is correct\n• Large videos take longer\n• Some platforms may require login\n\n🎯 Enhanced features:\n• High quality HD\n• Fast downloads\n• Advanced error handling\n• Conflict protection",
        "instagram_auth_error": "❌ Instagram video requires login\n\n📱 Try other platforms:\n• TikTok ✅\n• YouTube ✅\n• Facebook ✅\n• Twitter ✅\n• Reddit ✅\n\nOr try another Instagram link that might be public.",
        "network_error": "❌ Internet connection problem\n\n🔄 Please:\n• Check your internet connection\n• Try again in a moment\n• Verify the link works in browser",
        "video_unavailable": "❌ Video is currently unavailable\n\n💡 Possible reasons:\n• Video deleted or private\n• Temporary platform issue\n• Link expired or old\n\n🔄 Try another link or come back later",
        "quality_info": "🎥 Quality information:",
        "processing_advanced": "🚀 Advanced processing in progress...",
        "about": "ℹ️ About Bot",
        "about_text": "🎬 ISSAM Enhanced Test Bot\n\n🔥 Features:\n• Download from 1000+ platforms\n• 4 supported languages\n• Advanced error handling\n• Conflict protection\n• High quality HD\n• Fast downloads\n• Quality selection\n\n👨‍💻 Developer: ISSAM\n🧪 Test Version: v2.0\n📅 Last Update: November 2025",
        "quality_select": "🎥 Choose video quality:",
        "quality_ultra": "💎 Ultra Quality (1080p)",
        "quality_hd": "🔥 High Quality HD (720p)",
        "quality_standard": "📺 Standard Quality (480p)",
        "quality_low": "📱 Low Quality (360p)",
        "quality_audio": "🎵 High Quality Audio (320kbps MP3)",
        "quality_selected": "Quality selected:",
        "processing_quality": "⚙️ Processing with selected quality...",
    },
    "fa": {
        # يمكن تكميلها بنفس النصوص من الكود الأصلي إذا احتجتها
    },
    "fr": {
        # يمكن تكميلها كذلك
    },
}

user_languages = {}
user_quality_preferences = {}

# =========================
# Helpers
# =========================

def get_message(user_id, key):
    user_lang = user_languages.get(user_id, "ar")
    return MESSAGES[user_lang].get(key, MESSAGES["ar"][key])


def create_language_keyboard():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
        telebot.types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
        telebot.types.InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
    )
    return markup


def create_quality_keyboard(user_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton(get_message(user_id, "quality_ultra"), callback_data="quality_ultra"),
        telebot.types.InlineKeyboardButton(get_message(user_id, "quality_hd"), callback_data="quality_hd"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton(get_message(user_id, "quality_standard"), callback_data="quality_standard"),
        telebot.types.InlineKeyboardButton(get_message(user_id, "quality_low"), callback_data="quality_low"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton(get_message(user_id, "quality_audio"), callback_data="quality_audio"),
    )
    return markup


def create_main_keyboard(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        telebot.types.KeyboardButton(get_message(user_id, "help")),
        telebot.types.KeyboardButton(get_message(user_id, "about")),
    )
    markup.add(
        telebot.types.KeyboardButton(get_message(user_id, "quality_select")),
        telebot.types.KeyboardButton(get_message(user_id, "choose_language")),
    )
    return markup


def is_url(text: str) -> bool:
    return any(text.startswith(p) for p in ["http://", "https://", "www."])


def detect_error_type(error_message: str) -> str:
    e = error_message.lower()
    if "sign in to confirm you’re not a bot" in e or "sign in to confirm you're not a bot" in e:
        # حماية YouTube ضد البوتات
        return "video_unavailable"
    if any(
        keyword in e
        for keyword in ["login", "authentication", "sign in", "private", "unavailable", "empty media response"]
    ):
        return "instagram_auth_error"
    if any(keyword in e for keyword in ["network", "connection", "timeout", "unreachable"]):
        return "network_error"
    return "video_unavailable"


def get_quality_format(user_id: int) -> str:
    quality = user_quality_preferences.get(user_id, "ultra")
    logger.info(f"🎯 [Quality] user {user_id} uses: {quality}")

    if quality == "ultra":
        return "best[height>=720]/best"
    if quality == "hd":
        return "best[height<=720][height>=480]/worstvideo[height>=480]/best[height<=720]"
    if quality == "standard":
        return "best[height<=480][height>=360]/worstvideo[height>=360]/best[height<=480]"
    if quality == "low":
        return "worst[height<=360]/worstvideo/worst"
    if quality == "audio":
        return "bestaudio[filesize<20M]/bestaudio/best"
    return "best[height>=720]/best"


def process_video_url(url: str, user_id: int):
    """نسخة webhook من process_video_url ديالك"""
    try:
        format_selector = get_quality_format(user_id)
        quality_preference = user_quality_preferences.get(user_id, "ultra")

        Path("downloads").mkdir(exist_ok=True)

        ydl_opts = {
            "format": format_selector,
            "outtmpl": "downloads/%(title)s_%(format_id)s.%(ext)s",
            "noplaylist": True,
            "extract_flat": False,
            "writethumbnail": False,
            "writeinfojson": False,
            "ignoreerrors": False,
            "no_warnings": False,
            "embed_subs": False,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "listformats": False,
            "format_sort": ["res", "fps", "codec:h264", "size"],
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "referer": "https://www.instagram.com/",
            "retries": 3,
            "fragment_retries": 5,
            "skip_unavailable_fragments": True,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    "Mobile/15E148 Instagram 239.0.0.10.109"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-us",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
                "X-Requested-With": "XMLHttpRequest",
            },
        }

        if quality_preference == "audio":
            logger.info("🎵 [Audio] audio-only mode enabled")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"🔍 [Enhanced] extracting info: {url}")
            info = ydl.extract_info(url, download=False)

            if not info:
                logger.error("❌ failed to extract info")
                return None, get_message(user_id, "video_unavailable")

            # log first 5 formats (optional)
            if "formats" in info:
                logger.info("📊 [Quality Debug] available formats:")
                for fmt in info["formats"][:5]:
                    h = fmt.get("height", "unknown")
                    w = fmt.get("width", "unknown")
                    fs = fmt.get("filesize", 0)
                    size_mb = f"{fs/(1024*1024):.1f}MB" if fs else "unknown"
                    fid = fmt.get("format_id", "unknown")
                    logger.info(f"  🎥 {fid}: {w}x{h} - {size_mb}")

            filesize = info.get("filesize") or 0
            if filesize and filesize > 50 * 1024 * 1024:
                logger.warning(f"⚠️ file too large: {filesize/1024/1024:.1f} MB")
                return None, get_message(user_id, "too_large")

            logger.info("⬇️ [Enhanced] downloading video...")
            ydl.download([url])

        import glob

        downloads = glob.glob("downloads/*")
        logger.info(f"🔍 [Files] in downloads: {downloads}")

        if downloads:
            video_file = max(downloads, key=os.path.getctime)
            if Path(video_file).exists():
                size_mb = Path(video_file).stat().st_size / (1024 * 1024)
                logger.info(f"✅ downloaded: {video_file} ({size_mb:.1f} MB)")
                return video_file, None
            logger.error(f"❌ file missing: {video_file}")
            return None, get_message(user_id, "error")

        logger.error("❌ no downloaded files found")
        return None, get_message(user_id, "error")

    except Exception as e:
        error_message = str(e)
        logger.error(f"❌ [Enhanced] download error: {error_message}")
        error_type = detect_error_type(error_message)
        return None, get_message(user_id, error_type)


# =========================
# Flask webhook
# =========================

@app.route("/", methods=["GET"])
def index():
    return "ISSAM Enhanced Test Bot is running", 200


@app.route(WEBHOOK_PATH, methods=["POST"])
def telegram_webhook():
    if request.headers.get("content-type") == "application/json":
        json_str = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "", 200
    abort(403)


# =========================
# Handlers (start/help/about/quality/text)
# =========================

@bot.message_handler(commands=["start"])
def start_command(message):
    logger.info("DEBUG_START_HANDLER_FIRED")
    user_id = message.from_user.id
    user_languages[user_id] = "ar"
    if user_id not in user_quality_preferences:
        user_quality_preferences[user_id] = "ultra"

    bot.send_message(
        message.chat.id,
        get_message(user_id, "welcome"),
        reply_markup=create_language_keyboard(),
    )
    bot.send_message(
        message.chat.id,
        f"🎥 {get_message(user_id, 'quality_select')}\n\n🎯 الحالية: {get_message(user_id, 'quality_ultra')}",
        reply_markup=create_quality_keyboard(user_id),
    )
    bot.send_message(
        message.chat.id,
        f"📎 {get_message(user_id, 'send_link')}",
        reply_markup=create_main_keyboard(user_id),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def language_callback(call):
    user_id = call.from_user.id
    lang_code = call.data.split("_")[1]
    user_languages[user_id] = lang_code

    bot.edit_message_text(
        get_message(user_id, "language_set") + "\n\n" + get_message(user_id, "send_link"),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None,
    )
    bot.send_message(
        call.message.chat.id,
        "🎉",
        reply_markup=create_main_keyboard(user_id),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("quality_"))
def quality_callback(call):
    user_id = call.from_user.id
    quality_code = call.data.split("_")[1]
    user_quality_preferences[user_id] = quality_code

    quality_names = {
        "ultra": get_message(user_id, "quality_ultra"),
        "hd": get_message(user_id, "quality_hd"),
        "standard": get_message(user_id, "quality_standard"),
        "low": get_message(user_id, "quality_low"),
        "audio": get_message(user_id, "quality_audio"),
    }
    selected_quality = quality_names.get(quality_code, get_message(user_id, "quality_ultra"))

    bot.edit_message_text(
        f"✅ {get_message(user_id, 'quality_selected')} {selected_quality}\n\n{get_message(user_id, 'send_link')}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None,
    )
    bot.send_message(
        call.message.chat.id,
        "🎉",
        reply_markup=create_main_keyboard(user_id),
    )


@bot.message_handler(func=lambda m: get_message(m.from_user.id, "help") in (m.text or ""))
def help_command(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        get_message(user_id, "help_text"),
        reply_markup=create_main_keyboard(user_id),
    )


@bot.message_handler(func=lambda m: get_message(m.from_user.id, "about") in (m.text or ""))
def about_command(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        get_message(user_id, "about_text"),
        reply_markup=create_main_keyboard(user_id),
    )


@bot.message_handler(func=lambda m: get_message(m.from_user.id, "choose_language") in (m.text or ""))
def language_command(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        get_message(user_id, "choose_language"),
        reply_markup=create_language_keyboard(),
    )


@bot.message_handler(func=lambda m: get_message(m.from_user.id, "quality_select") in (m.text or ""))
def quality_command(message):
    user_id = message.from_user.id
    current_quality = user_quality_preferences.get(user_id, "ultra")
    quality_names = {
        "ultra": get_message(user_id, "quality_ultra"),
        "hd": get_message(user_id, "quality_hd"),
        "standard": get_message(user_id, "quality_standard"),
        "low": get_message(user_id, "quality_low"),
        "audio": get_message(user_id, "quality_audio"),
    }
    current_quality_name = quality_names.get(current_quality, get_message(user_id, "quality_ultra"))

    bot.send_message(
        message.chat.id,
        f"{get_message(user_id, 'quality_select')}\n\n🎯 الحالية: {current_quality_name}",
        reply_markup=create_quality_keyboard(user_id),
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = (message.text or "").strip()

    if not is_url(text):
        bot.send_message(
            message.chat.id,
            get_message(user_id, "invalid_url"),
            reply_markup=create_main_keyboard(user_id),
        )
        return

    current_quality = user_quality_preferences.get(user_id, "ultra")
    quality_names = {
        "ultra": get_message(user_id, "quality_ultra"),
        "hd": get_message(user_id, "quality_hd"),
        "standard": get_message(user_id, "quality_standard"),
        "low": get_message(user_id, "quality_low"),
        "audio": get_message(user_id, "quality_audio"),
    }
    quality_text = quality_names.get(current_quality, get_message(user_id, "quality_ultra"))

    processing_msg = bot.send_message(
        message.chat.id,
        f"{get_message(user_id, 'processing_quality')}\n🎯 {quality_text}",
    )

    try:
        Path("downloads").mkdir(exist_ok=True)

        bot.edit_message_text(
            get_message(user_id, "downloading"),
            message.chat.id,
            processing_msg.message_id,
        )

        video_file, error_message = process_video_url(text, user_id)

        if error_message:
            bot.edit_message_text(
                error_message,
                message.chat.id,
                processing_msg.message_id,
            )
            return

        if video_file and Path(video_file).exists():
            bot.edit_message_text(
                get_message(user_id, "uploading"),
                message.chat.id,
                processing_msg.message_id,
            )

            file_size = Path(video_file).stat().st_size / (1024 * 1024)
            current_quality = user_quality_preferences.get(user_id, "ultra")
            quality_info_map = {
                "ultra": "Ultra 1080p",
                "hd": "HD 720p",
                "standard": "480p",
                "low": "360p",
                "audio": "320kbps MP3",
            }
            quality_info = quality_info_map.get(current_quality, "Ultra 1080p")

            caption = (
                f"✅ {get_message(user_id, 'success')}\n\n"
                f"📁 الحجم: {file_size:.1f} MB\n"
                f"🎥 الجودة: {quality_info}\n"
                "🧪 ISSAM Enhanced Test Bot v2.0"
            )

            if current_quality == "audio" or video_file.endswith((".mp3", ".m4a", ".aac", ".opus")):
                with open(video_file, "rb") as audio:
                    bot.send_audio(
                        message.chat.id,
                        audio,
                        caption=caption,
                        reply_markup=create_main_keyboard(user_id),
                    )
            else:
                with open(video_file, "rb") as video:
                    bot.send_video(
                        message.chat.id,
                        video,
                        caption=caption,
                        reply_markup=create_main_keyboard(user_id),
                    )

            bot.delete_message(message.chat.id, processing_msg.message_id)

            try:
                Path(video_file).unlink()
                logger.info(f"🗑️ [Enhanced] deleted file: {video_file}")
            except Exception:
                pass
        else:
            bot.edit_message_text(
                get_message(user_id, "error"),
                message.chat.id,
                processing_msg.message_id,
            )

    except Exception as e:
        logger.error(f"❌ [Enhanced] general error: {e}")
        bot.edit_message_text(
            get_message(user_id, "error"),
            message.chat.id,
            processing_msg.message_id,
        )


# =========================
# Webhook setup & run
# =========================

def setup_webhook():
    logger.info("Removing old webhook")
    bot.remove_webhook()
    time.sleep(1)
    logger.info(f"Setting webhook to {WEBHOOK_URL}")
    bot.set_webhook(url=WEBHOOK_URL, max_connections=10)


if __name__ == "__main__":
    setup_webhook()
    logger.info(f"Starting Flask server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
