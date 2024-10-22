import os

class Config:
    MONGO_URI = "mongodb://localhost:27017/sms_management"
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'password'
    MYSQL_DB = 'sms_metrics'
    TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
    TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'
    JWT_SECRET_KEY = 'your_jwt_secret_key'