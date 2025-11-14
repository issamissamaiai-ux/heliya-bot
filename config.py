#!/usr/bin/env python3
"""
Configuration file for HOLAKO Bot
"""

import os
from typing import List

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin user IDs (replace with actual Telegram user IDs)
ADMIN_IDS: List[int] = [
    # Example: 123456789,
]

MAX_FILE_SIZE_MB = 50
DEFAULT_QUALITY = "best"
CLEANUP_INTERVAL_HOURS = 1

SUPPORTED_FORMATS = ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm"]

RATE_LIMIT_PER_USER = 10
DOWNLOADS_DIR = "downloads"

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
