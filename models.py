from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from datetime import datetime

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

class User(db.Model):
    """Model for storing user records."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class SMSSent(db.Model):
    """Model for storing SMS sent records."""
    id = db.Column(db.Integer, primary_key=True)
    country_operator = db.Column(db.String(50), nullable=False)
    success_rate = db.Column(db.Float, nullable=False)
    failures = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# MongoDB Connection
def get_mongo_db(app):
    """Get the MongoDB database instance."""
    try:
        mongo_client = MongoClient(app.config['MONGO_URI'])
        return mongo_client['sms_management']  # replace with your actual database name
    except (ConnectionError, ConfigurationError) as e:
        app.logger.error(f"MongoDB connection error: {e}")
        return None  # or handle this case as you see fit
