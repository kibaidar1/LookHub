import os
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Time zone configuration
TIME_ZONE = 'Europe/Moscow'

# Database configuration
DB_HOST = os.environ.get("DB_HOST", "localhost")  # Database host with localhost default
DB_PORT = os.environ.get("DB_PORT", "5432")  # Database port with default PostgreSQL port
DB_NAME = os.environ.get("POSTGRES_DB")  # Database name
DB_USER = os.environ.get("POSTGRES_USER")  # Database user
DB_PASS = os.environ.get("POSTGRES_PASSWORD")  # Database password

# File system paths
UPLOAD_IMAGES_DIR = BASE_DIR / "app" / "static" / "images"  # Directory for uploaded images
UPLOAD_IMAGES_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

# API configuration
API_HOST = os.environ.get("DOMAIN", "http://127.0.0.1")  # API base URL
API_KEY = os.environ.get("API_KEY", "supersecretapikey")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", '6379')

# JWT config
SECRET_KEY = os.environ.get("ADMIN_JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Hardcoded admin credentials
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# Flower settings
FLOWER_URL = "http://flower:5555/admin/flower"

# Celery settings
SENDING_LOOKS_SCHEDULE_HOURS = "*"
SENDING_LOOKS_SCHEDULE_MINUTE = "*/10"
