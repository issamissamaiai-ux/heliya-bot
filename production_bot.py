#!/usr/bin/env python3
"""
HOLAKO Download Bot - Webhook + Flask version for Render Web Service
"""

import os
import logging
import time
import threading
from urllib.parse import urlparse
from pathlib import Path

from flask import Flask, request, abort
import telebot
from telebot import types

# =========================
# Logging
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("HOLAKO_WEBHOOK")

# =========================
# Config
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN env variable is required")

# Render يعطي PORT فـ env
PORT = int(os.environ.get("PORT", 5000))

# هنا حط الدومين ديال Render ديالك بلا / فالنهاية
BASE_URL = os.getenv("BASE_URL", "https://heliya-bot-1.onrender.com")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = BASE_URL + WEBHOOK_PATH

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

user_data = {}

# =========================
# Messages (استعمل اللي عندك)
# =========================

MESSAGES = {
    "ar": {
        "welcome": "🎬 أهلاً {name}! أرسل رابط الفيديو للتحميل.",
        "processing": "⏳ جاري معالجة الرابط...",
        "invalid_url": "❌ أرسل رابط فيديو صالح.",
        "video_unavailable": "❌ الفيديو غير متاح، جرّب رابط آخر.",
        "success": "✅ تم التحميل!",
        "analyzing": "🔍 جاري تحليل الرابط...",
        "extracting": "📊 استخراج معلومات الفيديو...",
        "downloading": "⬇️ جاري التحميل...",
        "uploading": "📤 جاري الرفع...",
        "file_too_large": "❌ حجم الفيديو {size:.1f} MB أكبر من 50MB.",
    },
    "en": {
        "welcome": "🎬 Welcome {name}! Send a video link to download.",
        "processing": "⏳ Processing link...",
        "invalid_url": "❌ Please send a valid video URL.",
        "video_unavailable": "❌ Video unavailable, try another link.",
        "success": "✅ Download successful!",
        "analyzing": "🔍 Analyzing link...",
        "extracting": "📊 Extracting info...",
        "downloading": "⬇️ Downloading...",
        "uploading": "📤 Uploading...",
        "file_too_large": "❌ Video size {size:.1f} MB > 50MB.",
    },
}


def get_user_language(user_id: int) -> str:
    return user_data.get(user_id, {}).get("language", "ar")


def get_message(user_id: int, key: str, **kwargs) -> str:
    lang = get_user_language(user_id)
    message = MESSAGES.get(lang, MESSAGES["ar"]).get(key, MESSAGES["ar"][key])
    return message.format(**kwargs) if kwargs else message


def is_video_url(url: str) -> bool:
    video_domains = [
        "youtube.com",
        "youtu.be",
        "tiktok.com",
        "instagram.com",
        "facebook.com",
        "fb.watch",
        "twitter.com",
        "x.com",
        "reddit.com",
        "twitch.tv",
        "vimeo.com",
        "dailymotion.com",
    ]
    low = url.lower()
    return any(domain in low for domain in video_domains)


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


# =========================
# Flask webhook endpoint
# =========================

@app.route("/", methods=["GET"])
def index():
    return "HOLAKO Bot is running", 200


@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_str = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "", 200
    else:
        abort(403)


# =========================
# Bot handlers (نستعمل نفس المنطق ديالك)
# =========================

@bot.message_handler(commands=["start", "help"])
def start_command(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Friend"
    text = get_message(user_id, "welcome", name=user_name)
    bot.send_message(message.chat.id, text)


def process_video_url(message):
    try:
        import yt_dlp
    except ImportError:
        bot.send_message(
            message.chat.id,
            "❌ Video processing temporarily unavailable. Please try again later.",
        )
        return

    url = message.text.strip()
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Friend"

    processing_msg = bot.send_message(
        message.chat.id,
        f"🎬 {user_name}!\n\n" + get_message(user_id, "processing"),
    )

    try:
        preferred_quality = user_data.get(user_id, {}).get("preferred_quality", "best")

        bot.edit_message_text(
            get_message(user_id, "analyzing"),
            message.chat.id,
            processing_msg.message_id,
        )

        downloads_dir = Path("downloads")
        downloads_dir.mkdir(exist_ok=True)

        format_selector = "best[ext=mp4][filesize<50M]/best[filesize<50M]/best"
        if preferred_quality != "best" and preferred_quality.isdigit():
            format_selector = (
                f"best[height<={preferred_quality}][ext=mp4][filesize<50M]/"
                "best[filesize<50M]"
            )

        ydl_opts = {
            "format": format_selector,
            "outtmpl": str(downloads_dir / "%(title).50s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 20,
            "retries": 2,
            "fragment_retries": 2,
        }

        bot.edit_message_text(
            get_message(user_id, "extracting"),
            message.chat.id,
            processing_msg.message_id,
        )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                title = (info.get("title") or "Video")[:30]

                filesize = info.get("filesize") or info.get("filesize_approx")
                if filesize and filesize > 50 * 1024 * 1024:
                    bot.edit_message_text(
                        get_message(
                            user_id, "file_too_large", size=filesize / (1024 * 1024)
                        ),
                        message.chat.id,
                        processing_msg.message_id,
                    )
                    return

                bot.edit_message_text(
                    get_message(user_id, "downloading"),
                    message.chat.id,
                    processing_msg.message_id,
                )

                ydl.download([url])

                filename = ydl.prepare_filename(info)
                if not os.path.exists(filename):
                    base = os.path.splitext(filename)[0]
                    for ext in [".mp4", ".webm", ".mkv"]:
                        candidate = base + ext
                        if os.path.exists(candidate):
                            filename = candidate
                            break

                if os.path.exists(filename) and os.path.getsize(filename) > 0:
                    bot.edit_message_text(
                        get_message(user_id, "uploading"),
                        message.chat.id,
                        processing_msg.message_id,
                    )

                    with open(filename, "rb") as video_file:
                        bot.send_video(
                            message.chat.id,
                            video_file,
                            caption=f"🎬 {title}\n\n📥 Downloaded by HOLAKO Bot",
                            supports_streaming=True,
                            timeout=60,
                        )

                    bot.send_message(message.chat.id, get_message(user_id, "success"))

                    try:
                        bot.delete_message(message.chat.id, processing_msg.message_id)
                        os.remove(filename)
                    except Exception:
                        pass
                else:
                    bot.edit_message_text(
                        get_message(user_id, "video_unavailable"),
                        message.chat.id,
                        processing_msg.message_id,
                    )

            except yt_dlp.utils.DownloadError as e:
                logger.error(f"yt-dlp DownloadError: {e}")
                bot.edit_message_text(
                    get_message(user_id, "video_unavailable"),
                    message.chat.id,
                    processing_msg.message_id,
                )
            except Exception as e:
                logger.error(f"Unexpected download error: {e}")
                bot.edit_message_text(
                    get_message(user_id, "video_unavailable"),
                    message.chat.id,
                    processing_msg.message_id,
                )

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        bot.edit_message_text(
            get_message(user_id, "video_unavailable"),
            message.chat.id,
            processing_msg.message_id,
        )


@bot.message_handler(content_types=["text"])
def handle_text(message):
    text = message.text or ""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Friend"

    if is_video_url(text) or (is_valid_url(text) and text.startswith("http")):
        th = threading.Thread(target=process_video_url, args=(message,))
        th.daemon = True
        th.start()
    else:
        bot.send_message(
            message.chat.id,
            f"🤔 {user_name}!\n\n" + get_message(user_id, "invalid_url"),
        )


# =========================
# Main: setup webhook & run Flask
# =========================

def setup_webhook():
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL, max_connections=5)
    logger.info(f"Webhook set to {WEBHOOK_URL}")


if __name__ == "__main__":
    setup_webhook()
    logger.info(f"Starting Flask server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
