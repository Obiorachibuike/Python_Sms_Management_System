import os

class Config:
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sms_management.db")  # SQLite database by default
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/sms_management")  # MongoDB URI
    MYSQL_HOST = os.getenv("MYSQL_HOST", 'localhost')  # MySQL host
    MYSQL_USER = os.getenv("MYSQL_USER", 'root')  # MySQL user
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", 'password')  # MySQL password
    MYSQL_DB = os.getenv("MYSQL_DB", 'sms_metrics')  # MySQL database name

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", 'YOUR_TELEGRAM_BOT_TOKEN')  # Telegram bot token
    TELEGRAM_CHAT_ID = os.getenv("CHAT_ID", 'YOUR_TELEGRAM_CHAT_ID')  # Telegram chat ID

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", 'your_jwt_secret_key')  # JWT secret key
