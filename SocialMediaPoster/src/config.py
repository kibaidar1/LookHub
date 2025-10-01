import os
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# File system paths
UPLOAD_FILES_DIR = BASE_DIR / "src" / "static" / "temporary"  # Directory for uploaded images
UPLOAD_FILES_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

# Instagram configuration
INSTAGRAM_LOGIN = os.environ.get('INSTAGRAM_LOGIN')
INSTAGRAM_PASSWORD = os.environ.get('INSTAGRAM_PASSWORD')

# Telegram configuration
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Bot API token
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")  # Target channel ID



