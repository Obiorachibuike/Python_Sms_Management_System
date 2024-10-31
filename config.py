import os

class Config:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret')  # Default JWT secret
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'mysql+pymysql://root:@localhost/sms_management'
    )  # Default MySQL URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = os.getenv(
        'MONGO_URI', 
        "mongodb+srv://User:Fanthom456world@cluster0.paigpn8.mongodb.net/SMS_Management?retryWrites=true&w=majority"
    )  # Default MongoDB URI
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_telegram_bot_token')  # Default Telegram bot token
    CHAT_ID = os.getenv('CHAT_ID', 'your_chat_id')  # Default chat ID for Telegram
    PROMETHEUS_PORT = os.getenv('PROMETHEUS_PORT', 9091)  # Default Prometheus port
