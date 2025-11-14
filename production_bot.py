#!/usr/bin/env python3
"""
ISSAM Enhanced Test Bot - Render Webhook Version
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
# Messages
# =========================

MESSAGES = {
    "ar": {
        "welcome": "🎬 مرحباً بك في بوت ISSAM المحسن!\n\nأرسل أي رابط فيديو وسأحمله لك بدون علامة مائية.",
        "choose_language": "🌍 اختر لغتك / Choose Language:",
        "language_set": "✅ تم تعيين اللغة العربية!",
        "send_link": "📎 أرسل رابط الفيديو الذي تريد تحميله:",
        "processing": "⏳ جاري معالجة الرابط...",
        "processing_quality": "⚙️ جاري المعالجة بالجودة المختارة...",
        "downloading": "⬇️ جاري تحميل الفيديو...",
        "uploading": "⬆️ جاري رفع الفيديو...",
        "success": "✅ تم التحميل بنجاح!",
        "error": "❌ حدث خطأ أثناء التحميل. يرجى المحاولة مرة أخرى.",
        "invalid_url": "❌ رابط غير صحيح. أرسل رابط يبدأ بـ http أو https.",
        "too_large": "❌ حجم الفيديو كبير جداً (أكثر من 50 ميجا). جرب فيديو أصغر أو جودة أقل.",
        "unsupported": "❌ منصة غير مدعومة أو فيديو غير متاح.",
        "help": "🆘 مساعدة",
        "help_text": "📚 طريقة الاستخدام:\n\n1️⃣ أرسل رابط الفيديو\n2️⃣ اختر الجودة من الزر\n3️⃣ انتظر التحميل\n4️⃣ استلم الفيديو.",
        "about": "ℹ️ حول البوت",
        "about_text": "🤖 بوت ISSAM للتحميل من 1000+ منصة.",
        "instagram_auth_error": "❌ فيديو إنستغرام يتطلب تسجيل دخول أو غير متاح للعامة.",
        "network_error": "❌ مشكلة في الاتصال بالإنترنت. حاول لاحقاً.",
        "video_unavailable": "❌ الفيديو غير متاح حالياً. جرب رابطاً آخر.",
        "quality_select": "🎥 اختر جودة الفيديو:",
        "quality_ultra": "💎 جودة فائقة (1080p)",
        "quality_hd": "🔥 جودة عالية (720p)",
        "quality_standard": "📺 جودة عادية (480p)",
        "quality_low": "📱 جودة منخفضة (360p)",
        "quality_audio": "🎵 صوت فقط (MP3)",
        "quality_selected": "تم اختيار الجودة:",
    },
    "en": {
        "welcome": "🎬 Welcome to ISSAM Enhanced Download Bot!\n\nSend any video link and I'll download it without watermark.",
        "choose_language": "🌍 اختر لغتك / Choose Language:",
        "language_set": "✅ English language has been set!",
        "send_link": "📎 Send the video link you want to download:",
        "processing": "⏳ Processing link...",
        "processing_quality": "⚙️ Processing with selected quality...",
        "downloading": "⬇️ Downloading video...",
        "uploading": "⬆️ Uploading video...",
        "success": "✅ Downloaded successfully!",
        "error": "❌ An error occurred during download. Please try again.",
        "invalid_url": "❌ Invalid link. Please send a valid http/https link.",
        "too_large": "❌ Video is too large (over 50 MB). Try a smaller video or lower quality.",
        "unsupported": "❌ Unsupported platform or video not available.",
        "help": "🆘 Help",
        "help_text": "📚 How to use:\n\n1️⃣ Send video link\n2️⃣ Choose quality\n3️⃣ Wait for download\n4️⃣ Receive your video.",
        "about": "ℹ️ About Bot",
        "about_text": "🤖 ISSAM Enhanced Test Bot.",
        "instagram_auth_error": "❌ Instagram video requires login or is not public.",
        "network_error": "❌ Internet connection problem. Please try again later.",
        "video_unavailable": "❌ Video is currently unavailable. Try another link.",
        "quality_select": "🎥 Choose video quality:",
        "quality_ultra": "💎 Ultra (1080p)",
        "quality_hd": "🔥 HD (720p)",
        "quality_standard": "📺 Standard (480p)",
        "quality_low": "📱 Low (360p)",
        "quality_audio": "🎵 Audio only (MP3)",
        "quality_selected": "Quality selected:",
    },
    "fa": {},
    "fr": {},
}

user_languages = {}
user_quality_preferences = {}

# =========================
# Helpers
# =========================

def get_message(user_id, key):
    lang = user_languages.get(user_id, "ar")
    base = MESSAGES.get(lang, MESSAGES["ar"])
    return base.get(key, MESSAGES["ar"][key])


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
        telebot.types.InlineKeyboardButton(
            get_message(user_id, "quality_ultra"), callback_data="quality_ultra"
        ),
        telebot.types.InlineKeyboardButton(
            get_message(user_id, "quality_hd"), callback_data="quality_hd"
        ),
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            get_message(user_id, "quality_standard"), callback_data="quality_standard"
        ),
        telebot.types.InlineKeyboardButton(
            get_message(user_id, "quality_low"), callback_data="quality_low"
        ),
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            get_message(user_id, "quality_audio"), callback_data="quality_audio"
        )
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
    if any(
        k in e
        for k in [
            "login",
            "authentication",
            "sign in",
            "private",
            "unavailable",
            "empty media response",
        ]
    ):
        return "instagram_auth_error"
    if any(k in e for k in ["network", "connection", "timeout", "unreachable"]):
        return "network_error"
    return "video_unavailable"


def get_quality_format(user_id: int) -> str:
    quality = user_quality_preferences.get(user_id, "ultra")
    logger.info(f"[Quality] user {user_id} uses: {quality}")

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
    try:
        fmt = get_quality_format(user_id)
        quality_preference = user_quality_preferences.get(user_id, "ultra")

        Path("downloads").mkdir(exist_ok=True)

        ydl_opts = {
            "format": fmt,
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
            logger.info("[Audio] audio‑only mode enabled")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"[Enhanced] extracting info: {url}")
            info = ydl.extract_info(url, download=False)
            if not info:
                return None, get_message(user_id, "video_unavailable")

            filesize = info.get("filesize") or info.get("filesize_approx") or 0
            if filesize and filesize > 50 * 1024 * 1024:
                return None, get_message(user_id, "too_large")

            logger.info("[Enhanced] downloading...")
            ydl.download([url])

        import glob

        files = glob.glob("downloads/*")
        if not files:
            return None, get_message(user_id, "error")

        video_file = max(files, key=os.path.getctime)
        if not os.path.exists(video_file):
            return None, get_message(user_id, "error")

        logger.info(f"Downloaded file: {video_file}")
        return video_file, None

    except Exception as e:
        msg = str(e)
        logger.error(f"[Enhanced] download error: {msg}")
        etype = detect_error_type(msg)
        return None, get_message(user_id, etype)


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
# Handlers
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
        f"🎥 {get_message(user_id, 'quality_select')}\n\n🎯 الحالية: "
        f"{get_message(user_id, 'quality_ultra')}",
        reply_markup=create_quality_keyboard(user_id),
    )
    bot.send_message(
        message.chat.id,
        f"📎 {get_message(user_id, 'send_link')}",
        reply_markup=create_main_keyboard(user_id),
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
def language_callback(call):
    user_id = call.from_user.id
    lang_code = call.data.split("_", 1)[1]
    user_languages[user_id] = lang_code

    bot.edit_message_text(
        get_message(user_id, "language_set")
        + "\n\n"
        + get_message(user_id, "send_link"),
        call.message.chat.id,
        call.message.message_id,
    )
    bot.send_message(
        call.message.chat.id,
        "🎉",
        reply_markup=create_main_keyboard(user_id),
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("quality_"))
def quality_callback(call):
    user_id = call.from_user.id
    q_code = call.data.split("_", 1)[1]
    user_quality_preferences[user_id] = q_code

    quality_names = {
        "ultra": get_message(user_id, "quality_ultra"),
        "hd": get_message(user_id, "quality_hd"),
        "standard": get_message(user_id, "quality_standard"),
        "low": get_message(user_id, "quality_low"),
        "audio": get_message(user_id, "quality_audio"),
    }
    selected = quality_names.get(q_code, get_message(user_id, "quality_ultra"))

    bot.edit_message_text(
        f"✅ {get_message(user_id, 'quality_selected')} {selected}\n\n"
        f"{get_message(user_id, 'send_link')}",
        call.message.chat.id,
        call.message.message_id,
    )
    bot.send_message(
        call.message.chat.id,
        "🎉",
        reply_markup=create_main_keyboard(user_id),
    )


@bot.message_handler(func=lambda m: get_message(m.from_user.id, "help") in (m.text or ""))
def help_message(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        get_message(user_id, "help_text"),
        reply_markup=create_main_keyboard(user_id),
    )


@bot.message_handler(func=lambda m: get_message(m.from_user.id, "about") in (m.text or ""))
def about_message(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        get_message(user_id, "about_text"),
        reply_markup=create_main_keyboard(user_id),
    )


@bot.message_handler(func=lambda m: get_message(m.from_user.id, "choose_language") in (m.text or ""))
def lang_message(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        get_message(user_id, "choose_language"),
        reply_markup=create_language_keyboard(),
    )


@bot.message_handler(func=lambda m: get_message(m.from_user.id, "quality_select") in (m.text or ""))
def quality_message(message):
    user_id = message.from_user.id
    current = user_quality_preferences.get(user_id, "ultra")
    names = {
        "ultra": get_message(user_id, "quality_ultra"),
        "hd": get_message(user_id, "quality_hd"),
        "standard": get_message(user_id, "quality_standard"),
        "low": get_message(user_id, "quality_low"),
        "audio": get_message(user_id, "quality_audio"),
    }
    current_name = names.get(current, get_message(user_id, "quality_ultra"))
    bot.send_message(
        message.chat.id,
        f"{get_message(user_id, 'quality_select')}\n\n🎯 الحالية: {current_name}",
        reply_markup=create_quality_keyboard(user_id),
    )


@bot.message_handler(func=lambda m: True)
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
    names = {
        "ultra": get_message(user_id, "quality_ultra"),
        "hd": get_message(user_id, "quality_hd"),
        "standard": get_message(user_id, "quality_standard"),
        "low": get_message(user_id, "quality_low"),
        "audio": get_message(user_id, "quality_audio"),
    }
    q_text = names.get(current_quality, get_message(user_id, "quality_ultra"))

    processing = bot.send_message(
        message.chat.id,
        f"{get_message(user_id, 'processing_quality')}\n🎯 {q_text}",
    )

    try:
        Path("downloads").mkdir(exist_ok=True)

        bot.edit_message_text(
            get_message(user_id, "downloading"),
            message.chat.id,
            processing.message_id,
        )

        video_file, err = process_video_url(text, user_id)

        if err:
            bot.edit_message_text(
                err,
                message.chat.id,
                processing.message_id,
            )
            return

        if video_file and os.path.exists(video_file):
            bot.edit_message_text(
                get_message(user_id, "uploading"),
                message.chat.id,
                processing.message_id,
            )
            file_size = os.path.getsize(video_file) / (1024 * 1024)

            simple_quality = {
                "ultra": "Ultra 1080p",
                "hd": "HD 720p",
                "standard": "480p",
                "low": "360p",
                "audio": "320kbps MP3",
            }.get(current_quality, "Ultra 1080p")

            caption = (
                f"✅ {get_message(user_id, 'success')}\n\n"
                f"📁 Size: {file_size:.1f} MB\n"
                f"🎥 Quality: {simple_quality}\n"
                "🧪 ISSAM Enhanced Test Bot v2.0"
            )

            if current_quality == "audio" or video_file.lower().endswith(
                (".mp3", ".m4a", ".aac", ".opus")
            ):
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

            bot.delete_message(message.chat.id, processing.message_id)
            try:
                os.remove(video_file)
            except OSError:
                pass
        else:
            bot.edit_message_text(
                get_message(user_id, "error"),
                message.chat.id,
                processing.message_id,
            )

    except Exception as e:
        logger.error(f"[Enhanced] general error: {e}")
        bot.edit_message_text(
            get_message(user_id, "error"),
            message.chat.id,
            processing.message_id,
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
