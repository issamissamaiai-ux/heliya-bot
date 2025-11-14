#!/usr/bin/env python3
"""
HOLAKO Download Bot - Production Version with Full Multilingual Support
بوت هولاكو للإنتاج مع دعم كامل لأربع لغات

Optimized for free hosting platforms (Render, Railway, etc.)
مُحسّن للاستضافة المجانية مع الحفاظ على جميع اللغات
"""

import os
import logging
import time
import threading
from urllib.parse import urlparse
from pathlib import Path

import telebot
from telebot import types

# =========================
# Logging configuration
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("HOLAKO_PROD")

# =========================
# Bot configuration
# =========================

# IMPORTANT: token is read ONLY from environment variable BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

if not BOT_TOKEN:
    logger.error("BOT_TOKEN is not set. Please configure it in Render Environment Variables.")
    raise SystemExit("BOT_TOKEN is required")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# In‑memory user data (for production use DB if needed)
user_data = {}

# =========================
# Multilingual messages
# =========================

MESSAGES = {
    # Arabic & English كما في الكود اللي بعثتي (نفس المحتوى)
    # لو بغيت، خليه بالضبط كما عندك الآن لأنه صحيح
    # ...
}
# (خلي الباقي ديال MESSAGES كما في نسختك الأخيرة لأنه طويل ومزيان)

# =========================
# Helpers
# =========================


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
# Commands & callbacks
# =========================


@bot.message_handler(commands=["start"])
def start_command(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Friend"

    if user_id not in user_data or "language" not in user_data[user_id]:
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
            reply_markup=markup,
        )
    else:
        show_welcome_message(message.chat.id, user_name, user_id)


def show_welcome_message(chat_id: int, user_name: str, user_id: int):
    welcome_text = get_message(user_id, "welcome", name=user_name)

    markup = types.InlineKeyboardMarkup()
    help_btn = types.InlineKeyboardButton(
        get_message(user_id, "help_button"), callback_data="help"
    )
    quality_btn = types.InlineKeyboardButton(
        get_message(user_id, "quality_button"), callback_data="quality"
    )
    lang_btn = types.InlineKeyboardButton(
        get_message(user_id, "language_button"), callback_data="language"
    )

    markup.row(help_btn)
    markup.row(quality_btn)
    markup.row(lang_btn)

    bot.send_message(chat_id, welcome_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name or "Friend"

    try:
        # ... نفس الكود ديال callback اللي عندك (quality/lang/help)
        # ما يحتاجش تغيير
        pass

    except Exception as e:
        logger.error(f"Callback handler error: {e}")
        bot.answer_callback_query(call.id, "Error occurred")


# =========================
# Video processing
# =========================


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


# =========================
# Text handler
# =========================


@bot.message_handler(content_types=["text"])
def handle_text(message):
    text = message.text or ""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Friend"

    if user_id not in user_data or "language" not in user_data[user_id]:
        start_command(message)
        return

    if is_video_url(text) or (is_valid_url(text) and text.startswith("http")):
        thread = threading.Thread(target=process_video_url, args=(message,))
        thread.daemon = True
        thread.start()
    else:
        bot.send_message(
            message.chat.id,
            f"🤔 {user_name}!\n\n" + get_message(user_id, "invalid_url"),
        )


# =========================
# Main
# =========================


def main():
    print("🎬 Starting HOLAKO Download Bot - Production...")
    logger.info("HOLAKO Bot starting with infinity_polling")

    try:
        bot.infinity_polling(
            timeout=30,
            long_polling_timeout=10,
            none_stop=True,
            interval=1,
            allowed_updates=None,
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        time.sleep(5)
        main()  # auto‑restart


if __name__ == "__main__":
    main()
