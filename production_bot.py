#!/usr/bin/env python3
"""
ISSAM Bot - Webhook + Flask version for Render Web Service
"""

import os
import telebot
import yt_dlp
import logging
import time
import threading
import signal
import sys
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, request, abort

# =========================
# Config
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN env variable is required")

# Render يعطي PORT فـ env
PORT = int(os.environ.get("PORT", 5000))

# BASE_URL = رابط خدمة Render ديالك، مثلاً:
# https://heliya-bot-1.onrender.com
BASE_URL = os.getenv("BASE_URL", "https://heliya-bot-1.onrender.com")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = BASE_URL.rstrip("/") + WEBHOOK_PATH

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
app = Flask(__name__)

bot_running = True

# =========================
# Logging
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("ISSAM_WEBHOOK")

# =========================
# Messages & languages
# (ناخدو نفس القواميس اللي بعتّي، مختصرين هنا)
# =========================

MESSAGES = {
    "ar": {
        "welcome": "🎬 مرحباً بك في بوت ISSAM للتحميل!\n\n💫 أرسل لي رابط فيديو من أي منصة وسأقوم بتحميله لك بدون علامة مائية!\n\nالمنصات المدعومة:\n• YouTube 📺\n• TikTok 🎵\n• Instagram 📸\n• Facebook 📘\n• Twitter 🐦\n• وأكثر من 1000 منصة أخرى!\n\nاختر لغتك:",
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
        "help": "🆘 مساعدة",
        "help_text": "📚 كيفية استخدام البوت:\n\n1️⃣ أرسل رابط الفيديو\n2️⃣ انتظر التحميل\n3️⃣ احصل على الفيديو!\n\n💡 نصائح:\n• تأكد من أن الرابط صحيح\n• الفيديوهات الكبيرة تحتاج وقت أطول\n• بعض المنصات قد تتطلب تسجيل دخول",
        "instagram_auth_error": "❌ فيديو الإنستغرام يتطلب تسجيل دخول\n\n📱 حاول استخدام منصات أخرى:\n• TikTok ✅\n• YouTube ✅\n• Facebook ✅\n• Twitter ✅\n\nأو جرب رابط إنستغرام آخر قد يكون عام.",
        "network_error": "❌ مشكلة في الاتصال بالإنترنت\n\n🔄 يرجى:\n• التأكد من اتصال الإنترنت\n• المحاولة مرة أخرى بعد قليل\n• التحقق من أن الرابط يعمل في المتصفح",
        "video_unavailable": "❌ الفيديو غير متاح حالياً\n\n💡 الأسباب المحتملة:\n• الفيديو محذوف أو خاص\n• مشكلة مؤقتة في المنصة\n• الرابط قديم أو منتهي الصلاحية\n\n🔄 جرب رابط آخر أو عد لاحقاً",
    },
    "en": {
        "welcome": "🎬 Welcome to ISSAM Download Bot!\n\n💫 Send me a video link from any platform and I'll download it without watermark!\n\nSupported Platforms:\n• YouTube 📺\n• TikTok 🎵\n• Instagram 📸\n• Facebook 📘\n• Twitter 🐦\n• And 1000+ other platforms!\n\nChoose your language:",
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
        "help": "🆘 Help",
        "help_text": "📚 How to use the bot:\n\n1️⃣ Send video link\n2️⃣ Wait for download\n3️⃣ Get your video!\n\n💡 Tips:\n• Make sure the link is correct\n• Large videos take longer\n• Some platforms may require login",
        "instagram_auth_error": "❌ Instagram video requires login\n\n📱 Try other platforms:\n• TikTok ✅\n• YouTube ✅\n• Facebook ✅\n• Twitter ✅\n\nOr try another Instagram link that might be public.",
        "network_error": "❌ Internet connection problem\n\n🔄 Please:\n• Check your internet connection\n• Try again in a moment\n• Verify the link works in browser",
        "video_unavailable": "❌ Video is currently unavailable\n\n💡 Possible reasons:\n• Video deleted or private\n• Temporary platform issue\n• Link expired or old\n\n🔄 Try another link or come back later",
    },
    # يمكنك إضافة fa و fr بالكامل كما في كودك الأصلي
}

user_languages = {}


def get_message(user_id, key):
    user_lang = user_languages.get(user_id, "ar")
    base = MESSAGES.get(user_lang, MESSAGES["ar"])
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


def create_main_keyboard(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        telebot.types.KeyboardButton(get_message(user_id, "help")),
        telebot.types.KeyboardButton(get_message(user_id, "choose_language")),
    )
    return markup


def is_url(text: str) -> bool:
    return any(text.startswith(p) for p in ["http://", "https://", "www."])


def detect_error_type(error_message: str) -> str:
    e = error_message.lower()
    if any(k in e for k in ["login", "authentication", "sign in", "private", "unavailable", "empty media response"]):
        return "instagram_auth_error"
    if any(k in e for k in ["network", "connection", "timeout", "unreachable"]):
        return "network_error"
    return "video_unavailable"


def process_video_url(url: str, user_id: int):
    try:
        ydl_opts = {
            "format": "best[filesize<50M]/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "noplaylist": True,
            "extract_flat": False,
            "writethumbnail": False,
            "writeinfojson": False,
            "ignoreerrors": False,
            "no_warnings": False,
            "extractaudio": False,
            "audioformat": "mp3",
            "embed_subs": False,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
            "referer": "https://www.instagram.com/",
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    "Mobile/15E148 Instagram 105.0.0.11.118 "
                    "(iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-us",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
            },
        }

        Path("downloads").mkdir(exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"🔍 Extracting info: {url}")
            info = ydl.extract_info(url, download=False)

            if not info:
                logger.error("No info extracted")
                return None, get_message(user_id, "video_unavailable")

            filesize = info.get("filesize") or info.get("filesize_approx") or 0
            if filesize and filesize > 50 * 1024 * 1024:
                logger.warning(f"File too large: {filesize}")
                return None, get_message(user_id, "too_large")

            logger.info("⬇️ Downloading video...")
            ydl.download([url])

        import glob

        files = glob.glob("downloads/*")
        if not files:
            return None, get_message(user_id, "error")

        video_file = max(files, key=os.path.getctime)
        logger.info(f"✅ Downloaded file: {video_file}")
        return video_file, None

    except Exception as e:
        msg = str(e)
        logger.error(f"Download error: {msg}")
        etype = detect_error_type(msg)
        return None, get_message(user_id, etype)


# =========================
# Flask webhook endpoints
# =========================

@app.route("/", methods=["GET"])
def index():
    return "ISSAM Bot is running", 200


@app.route(WEBHOOK_PATH, methods=["POST"])
def telegram_webhook():
    if request.headers.get("content-type") == "application/json":
        json_str = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "", 200
    abort(403)


# =========================
# Bot handlers (نفس منطق كودك لكن بدون polling)
# =========================

@bot.message_handler(commands=["start"])
def start_command(message):
    user_id = message.from_user.id
    user_languages[user_id] = "ar"
    logger.info(f"New user: {message.from_user.first_name} ({user_id})")

    bot.send_message(
        message.chat.id,
        get_message(user_id, "welcome"),
        reply_markup=create_language_keyboard(),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def language_callback(call):
    user_id = call.from_user.id
    lang_code = call.data.split("_")[1]
    user_languages[user_id] = lang_code
    logger.info(f"User {user_id} chose lang {lang_code}")

    bot.edit_message_text(
        get_message(user_id, "language_set") + "\n\n" + get_message(user_id, "send_link"),
        call.message.chat.id,
        call.message.message_id,
    )

    bot.send_message(
        call.message.chat.id,
        "🎉",
        reply_markup=create_main_keyboard(user_id),
    )


@bot.message_handler(func=lambda message: get_message(message.from_user.id, "help") in message.text)
def help_command(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        get_message(user_id, "help_text"),
        reply_markup=create_main_keyboard(user_id),
    )


@bot.message_handler(func=lambda message: get_message(message.from_user.id, "choose_language") in message.text)
def lang_command(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        get_message(user_id, "choose_language"),
        reply_markup=create_language_keyboard(),
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

    processing_msg = bot.send_message(
        message.chat.id,
        get_message(user_id, "processing"),
    )

    try:
        logger.info(f"Processing URL from {user_id}: {text}")
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

        if video_file and os.path.exists(video_file):
            bot.edit_message_text(
                get_message(user_id, "uploading"),
                message.chat.id,
                processing_msg.message_id,
            )

            with open(video_file, "rb") as video:
                bot.send_video(
                    message.chat.id,
                    video,
                    caption=f"✅ {get_message(user_id, 'success')}\n\n🎬 @holako_download_bot - ISSAM Bot",
                    reply_markup=create_main_keyboard(user_id),
                )

            bot.delete_message(message.chat.id, processing_msg.message_id)
            try:
                os.remove(video_file)
            except OSError:
                pass
        else:
            bot.edit_message_text(
                get_message(user_id, "error"),
                message.chat.id,
                processing_msg.message_id,
            )

    except Exception as e:
        logger.error(f"General error: {e}")
        bot.edit_message_text(
            get_message(user_id, "error"),
            message.chat.id,
            processing_msg.message_id,
        )


# =========================
# Webhook setup & run
# =========================

def setup_webhook():
    logger.info("Removing old webhook (if any)")
    bot.remove_webhook()
    time.sleep(1)
    logger.info(f"Setting webhook to: {WEBHOOK_URL}")
    bot.set_webhook(url=WEBHOOK_URL, max_connections=10)


if __name__ == "__main__":
    setup_webhook()
    logger.info(f"Starting Flask server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
