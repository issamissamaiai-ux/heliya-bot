#!/usr/bin/env python3
"""
ISSAM Bot - Webhook + Flask + Quality Selection
"""

import os
import telebot
import yt_dlp
import logging
import time
import threading
from pathlib import Path
from flask import Flask, request, abort

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
)
logger = logging.getLogger("ISSAM_WEBHOOK")

# =========================
# Messages & state
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
        "too_large": "❌ حجم الفيديو كبير جداً (أكثر من 50 ميجا). جرب فيديو أصغر أو جودة أقل.",
        "help": "🆘 مساعدة",
        "help_text": "📚 كيفية استخدام البوت:\n\n1️⃣ أرسل رابط الفيديو\n2️⃣ اختر الجودة من /quality\n3️⃣ انتظر التحميل\n4️⃣ احصل على الفيديو!\n\n💡 نصائح:\n• تأكد من أن الرابط صحيح\n• الفيديوهات الكبيرة تحتاج وقت أطول\n• بعض منصات إنستغرام قد تتطلب تسجيل دخول",
        "instagram_auth_error": "❌ فيديو الإنستغرام يتطلب تسجيل دخول\n\n📱 حاول استخدام منصات أخرى:\n• TikTok ✅\n• YouTube ✅\n• Facebook ✅\n• Twitter ✅\n\nأو جرب رابط إنستغرام آخر قد يكون عام.",
        "network_error": "❌ مشكلة في الاتصال بالإنترنت\n\n🔄 يرجى التأكد من اتصال الإنترنت ثم المحاولة لاحقاً",
        "video_unavailable": "❌ الفيديو غير متاح حالياً\n\n💡 الأسباب المحتملة:\n• الفيديو محذوف أو خاص\n• مشكلة مؤقتة في المنصة\n• الرابط قديم أو منتهي الصلاحية\n\n🔄 جرب رابط آخر.",
        "quality_title": "🎥 اختر جودة التحميل:",
    },
    "en": {
        "welcome": "🎬 Welcome to ISSAM Download Bot!\n\n💫 Send me a video link and I'll download it without watermark!\n\nSupported:\n• YouTube 📺\n• TikTok 🎵\n• Instagram 📸 (public only)\n• Facebook 📘\n• Twitter 🐦\n• And 1000+ more!\n\nChoose your language:",
        "choose_language": "🌍 اختر لغتك / Choose Language:",
        "language_set": "✅ English language has been set!",
        "send_link": "📎 Send the video link you want to download:",
        "processing": "⏳ Processing the link...",
        "downloading": "⬇️ Downloading video...",
        "uploading": "⬆️ Uploading video...",
        "success": "✅ Downloaded successfully!",
        "error": "❌ An error occurred during download. Please try again.",
        "invalid_url": "❌ Invalid link. Please send a valid link.",
        "too_large": "❌ Video file is too large (over 50MB). Try a smaller video or lower quality.",
        "help": "🆘 Help",
        "help_text": "📚 How to use:\n\n1️⃣ Send video link\n2️⃣ Optional: /quality to choose preferred quality\n3️⃣ Wait for download\n4️⃣ Get your video!\n\n💡 Notes:\n• Make sure the link is correct\n• Large videos take longer\n• Some Instagram reels require login and cannot be downloaded.",
        "instagram_auth_error": "❌ Instagram video requires login\n\n📱 Try other platforms (TikTok / YouTube / Facebook / Twitter) or another public Instagram link.",
        "network_error": "❌ Internet connection problem\n\n🔄 Check your connection and try again later.",
        "video_unavailable": "❌ Video is currently unavailable.\n\nPossible reasons: deleted, private or temporary platform issue.\n\n🔄 Try another link.",
        "quality_title": "🎥 Choose download quality:",
    },
}

user_languages = {}          # user_id -> "ar"/"en"/"fa"/"fr"
user_quality = {}            # user_id -> "360"/"480"/"720"/"1080"/"best"

QUALITY_OPTIONS = {
    "360": "⚡ 360p Fast",
    "480": "📱 480p",
    "720": "📺 720p HD",
    "1080": "🎬 1080p Full HD",
    "best": "🌟 Best available",
}


def get_message(user_id, key):
    lang = user_languages.get(user_id, "ar")
    base = MESSAGES.get(lang, MESSAGES["ar"])
    return base.get(key, MESSAGES["ar"][key])


def create_language_keyboard():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        telebot.types.InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
        telebot.types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
    )
    kb.add(
        telebot.types.InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
        telebot.types.InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
    )
    return kb


def create_main_keyboard(user_id):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        telebot.types.KeyboardButton(get_message(user_id, "help")),
        telebot.types.KeyboardButton("/quality"),
    )
    return kb


def create_quality_keyboard():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        telebot.types.InlineKeyboardButton("⚡ 360p", callback_data="q_360"),
        telebot.types.InlineKeyboardButton("📱 480p", callback_data="q_480"),
    )
    kb.add(
        telebot.types.InlineKeyboardButton("📺 720p", callback_data="q_720"),
        telebot.types.InlineKeyboardButton("🎬 1080p", callback_data="q_1080"),
    )
    kb.add(
        telebot.types.InlineKeyboardButton("🌟 Best", callback_data="q_best"),
    )
    return kb


def is_url(text: str) -> bool:
    return any(text.startswith(p) for p in ["http://", "https://", "www."])


def detect_error_type(error_message: str) -> str:
    e = error_message.lower()
    if any(k in e for k in ["login", "authentication", "sign in", "private", "empty media response"]):
        return "instagram_auth_error"
    if any(k in e for k in ["network", "connection", "timeout", "unreachable"]):
        return "network_error"
    return "video_unavailable"


def build_format_selector(quality: str) -> str:
    # يستعمل height<=... مع حد الحجم 50MB
    if quality == "360":
        return "bestvideo[height<=360]+bestaudio/best[height<=360]"
    if quality == "480":
        return "bestvideo[height<=480]+bestaudio/best[height<=480]"
    if quality == "720":
        return "bestvideo[height<=720]+bestaudio/best[height<=720]"
    if quality == "1080":
        return "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    return "bestvideo+bestaudio/best"


def process_video_url(url: str, user_id: int):
    quality = user_quality.get(user_id, "best")
    fmt = build_format_selector(quality)

    try:
        Path("downloads").mkdir(exist_ok=True)

        ydl_opts = {
            "format": fmt,
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": False,
            "socket_timeout": 20,
            "retries": 2,
            "fragment_retries": 2,
            # headers خاصة بالإنستغرام
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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"🔍 Extracting info: {url}")
            info = ydl.extract_info(url, download=False)

            if not info:
                return None, get_message(user_id, "video_unavailable")

            filesize = info.get("filesize") or info.get("filesize_approx") or 0
            if filesize and filesize > 50 * 1024 * 1024:
                return None, get_message(user_id, "too_large")

            logger.info("⬇️ Downloading...")
            ydl.download([url])

        import glob

        files = glob.glob("downloads/*")
        if not files:
            return None, get_message(user_id, "error")

        video_file = max(files, key=os.path.getctime)
        return video_file, None

    except Exception as e:
        msg = str(e)
        logger.error(f"Download error: {msg}")
        etype = detect_error_type(msg)
        return None, get_message(user_id, etype)


# =========================
# Flask webhook
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
# Handlers
# =========================

@bot.message_handler(commands=["start"])
def start_cmd(message):
    user_id = message.from_user.id
    user_languages[user_id] = "ar"
    user_quality[user_id] = "best"
    bot.send_message(
        message.chat.id,
        get_message(user_id, "welcome"),
        reply_markup=create_language_keyboard(),
    )


@bot.message_handler(commands=["quality"])
def quality_cmd(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        get_message(user_id, "quality_title"),
        reply_markup=create_quality_keyboard(),
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("q_"))
def quality_callback(call):
    user_id = call.from_user.id
    q = call.data.split("_", 1)[1]
    user_quality[user_id] = q
    txt = QUALITY_OPTIONS.get(q, q)
    bot.edit_message_text(
        f"✅ {txt}",
        call.message.chat.id,
        call.message.message_id,
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
def lang_callback(call):
    user_id = call.from_user.id
    lang = call.data.split("_", 1)[1]
    user_languages[user_id] = lang
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


@bot.message_handler(func=lambda m: get_message(m.from_user.id, "help") in (m.text or ""))
def help_msg(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        get_message(user_id, "help_text"),
        reply_markup=create_main_keyboard(user_id),
    )


@bot.message_handler(func=lambda m: True)
def text_handler(message):
    user_id = message.from_user.id
    text = (message.text or "").strip()

    if not is_url(text):
        bot.send_message(
            message.chat.id,
            get_message(user_id, "invalid_url"),
            reply_markup=create_main_keyboard(user_id),
        )
        return

    processing = bot.send_message(
        message.chat.id,
        get_message(user_id, "processing"),
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
            with open(video_file, "rb") as f:
                bot.send_video(
                    message.chat.id,
                    f,
                    caption=f"✅ {get_message(user_id, 'success')}\n\n🎬 @holako_download_bot - ISSAM Bot",
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
        logger.error(f"General error: {e}")
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
