import os
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from metrics import Metrics
from telegram_bot import TelegramBot
from auth import Auth
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)  # Enables Cross-Origin Resource Sharing

# Load configuration from environment variables
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'default_secret')  # Use environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sms_management.db')  # SQLite by default
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications to save memory

jwt = JWTManager(app)  # Initialize JWT Manager for authentication
db = SQLAlchemy(app)  # Initialize SQLAlchemy for database interactions

# Initialize metrics and Telegram bot
metrics = Metrics()
telegram_bot = TelegramBot(app.config['TELEGRAM_BOT_TOKEN'], app.config['CHAT_ID'])

# Database model for CountryOperator
class CountryOperator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country_operator = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<CountryOperator {self.country_operator}>"

# Create database tables before the first request
@app.before_first_request
def create_tables():
    db.create_all()  # Creates database tables

# Endpoint for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:  # Validate input
        return jsonify({"msg": "Username and password are required"}), 400

    auth = Auth()  # Instantiate Auth class
    if auth.authenticate(username, password):  # Authenticate user
        access_token = create_access_token(identity=username)  # Create JWT token
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401  # Return error if authentication fails

# Endpoint to send SMS
@app.route('/sms/send', methods=['POST'])
@jwt_required()  # Protect this endpoint with JWT
def send_sms():
    data = request.json
    country_operator = data.get('country_operator')
    phone_number = data.get('phone_number')
    proxy = data.get('proxy')

    session_name = f"program1_{country_operator}"  # Create a session name for the SMS sending program
    # Start a new screen session for sending SMS
    subprocess.Popen(['screen', '-dmS', session_name, 'python', 'sms_program.py', phone_number, proxy])

    return jsonify({"msg": "SMS sending started"}), 200  # Return success message

# Endpoint to retrieve real-time metrics
@app.route('/metrics', methods=['GET'])
@jwt_required()  # Protect this endpoint with JWT
def get_metrics():
    return jsonify(metrics.get_metrics()), 200  # Return metrics data

# Endpoint to add country-operator pair
@app.route('/country-operator', methods=['POST'])
@jwt_required()  # Protect this endpoint with JWT
def add_country_operator():
    data = request.json
    country_operator = data.get('country_operator')

    if not country_operator:  # Validate input
        return jsonify({"msg": "Country operator is required"}), 400

    new_operator = CountryOperator(country_operator=country_operator)

    try:
        db.session.add(new_operator)  # Add new operator to the session
        db.session.commit()  # Commit the session to save changes
        return jsonify({"msg": "Country-operator added"}), 201  # Return success message
    except Exception as e:
        db.session.rollback()  # Rollback if there’s an error
        return jsonify({"msg": str(e)}), 400  # Return error message

# Endpoint to delete a country-operator pair
@app.route('/country-operator/<country_operator>', methods=['DELETE'])
@jwt_required()  # Protect this endpoint with JWT
def delete_country_operator(country_operator):
    operator = CountryOperator.query.filter_by(country_operator=country_operator).first()
    if operator:
        db.session.delete(operator)  # Delete the operator
        db.session.commit()  # Commit the session to save changes
        return jsonify({"msg": "Country-operator deleted"}), 200  # Return success message
    return jsonify({"msg": "Country-operator not found"}), 404  # Return not found message

# Custom error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"msg": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"msg": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Run the Flask app
