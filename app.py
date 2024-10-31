import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_graphql import GraphQLView  # Import GraphQLView for the GraphQL endpoint
from config import Config
from routes import routes  # Ensure routes.py is correctly structured to be imported
from metrics import Metrics
from telegram_bot import TelegramBot
from models import db, get_mongo_db
from schema import schema  # Import your GraphQL schema

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from Config class

# Enable CORS for the specified origin (adjust as needed)
CORS(app, resources={r"/*": {"origins": "http://localhost:5175"}})

# Initialize SQLAlchemy
db = SQLAlchemy(app)  # SQLAlchemy for database interactions

# Setup MongoDB
with app.app_context():
    mongo_db = get_mongo_db(app)  # Get MongoDB database instance

# Initialize JWT and SocketIO
jwt = JWTManager(app)  # JWT for authentication
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5175")  # Allow CORS for Socket.IO

# Initialize metrics and Telegram bot
metrics = Metrics()  # Start Prometheus metrics server
telegram_bot = TelegramBot(app.config['TELEGRAM_BOT_TOKEN'], app.config['CHAT_ID'])

# Register routes from routes.py
app.register_blueprint(routes)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# Create database tables before the first request
@app.before_request
def create_tables():
    db.create_all()  # Creates all database tables

# GraphQL route
app.add_url_rule(
    '/graphql', 
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)  # Enable GraphiQL interface
)

# Custom error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"msg": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"msg": "Internal server error"}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)  # Run the Flask app
