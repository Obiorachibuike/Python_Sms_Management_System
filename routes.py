from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import jwt_required
from flask_mail import Mail, Message
from models import SMSSent, db, get_mongo_db, User
from services import ProcessManager
from metrics import Metrics
from auth import Auth
from telegram_bot import TelegramBot
from sqlalchemy.exc import IntegrityError
import os
import bcrypt
import re
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables from a .env file
load_dotenv()

# Initialize components
routes = Blueprint('routes', __name__)
process_manager = ProcessManager()
metrics = Metrics()

# Ensure that SECRET_KEY is obtained from the environment variable
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    raise ValueError("SECRET_KEY environment variable is not set. Please set it.")

# Initialize the serializer for generating and verifying tokens
serializer = URLSafeTimedSerializer(secret_key)

# Initialize Telegram bot and mail services
telegram_bot = TelegramBot(os.getenv('TELEGRAM_BOT_TOKEN'), os.getenv('CHAT_ID'))
mail = Mail()  # Initialize Flask-Mail

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Centralized response utility for consistent API responses
def response(success=True, message="", data=None, status=200):
    return jsonify({
        "success": success,
        "message": message,
        "data": data
    }), status

# Password complexity check function
def is_valid_password(password):
    """Check if the password meets complexity requirements."""
    if len(password) < 8:  # Minimum length
        return False
    if not re.search("[a-z]", password):  # At least one lowercase letter
        return False
    if not re.search("[A-Z]", password):  # At least one uppercase letter
        return False
    if not re.search("[0-9]", password):  # At least one digit
        return False
    if not re.search("[@#$%^&+=]", password):  # At least one special character
        return False
    return True

# Initialize Auth service
auth_service = Auth()

# Signup route for user registration
@routes.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')  # Get email from request

    if not username or not password or not email:
        return response(success=False, message="Username, password, and email are required", status=400)

    if not is_valid_password(password):
        return response(success=False, message="Password does not meet complexity requirements", status=400)

    # Hash the password before storing
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    new_user = User(username=username, password=hashed_password, email=email)
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return response(success=False, message="Username or email already exists", status=400)
    except Exception as e:
        db.session.rollback()
        return response(success=False, message=str(e), status=500)

    # Generate a verification token and send verification email
    token = generate_verification_token(new_user.email)
    send_verification_email(new_user.email, token)

    return response(success=True, message="User created successfully. Please verify your email.", status=201)

# Email verification logic
def send_verification_email(user_email, token):
    """Send verification email."""
    msg = Message('Email Verification', sender='noreply@example.com', recipients=[user_email])
    msg.body = f'Please verify your email by clicking on the following link: {url_for("routes.verify_email", token=token, _external=True)}'
    mail.send(msg)

def generate_verification_token(email):
    """Generate a verification token."""
    return serializer.dumps(email, salt=os.getenv('SECURITY_PASSWORD_SALT'))

def verify_token(token):
    """Verify the token."""
    try:
        email = serializer.loads(token, salt=os.getenv('SECURITY_PASSWORD_SALT'), max_age=3600)  # Token valid for 1 hour
    except Exception:
        return False
    return email

@routes.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    email = verify_token(token)
    if not email:
        return response(success=False, message="Invalid or expired token", status=400)
    
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_verified = True
        db.session.commit()
        return response(success=True, message="Email verified successfully", status=200)

    return response(success=False, message="User not found", status=404)

@routes.route('/login', methods=['POST'])
def login():
    # Ensure to log the raw request data for debugging
    data = request.json
    print("Request data:", data)  # Debugging line to see the raw data
    
    email = data.get('email')
    password = data.get('password')
    
    print("Email:", email, "Password:", password)  # Debugging line

    # Check for missing fields
    if not email or not password:
        return response(success=False, message="Email and password are required", status=400)

    # Authenticate user
    user = auth_service.authenticate(email, password)
    
    if user:
        access_token = auth_service.create_access_token(user)  # Create access token
        return response(success=True, data={"access_token": access_token}, status=200)

    return response(success=False, message="Bad email or password", status=401)

# CRUD for CountryOperator (in MongoDB)
@routes.route('/country-operator', methods=['POST'])
@jwt_required()
def add_country_operator():
    data = request.json
    country_operator = data.get('country_operator')
    high_priority = data.get('high_priority', False)

    if not country_operator:
        return response(success=False, message="Country operator is required", status=400)

    # Add to MongoDB
    mongo_db = get_mongo_db()
    mongo_db.country_operators.insert_one({"country_operator": country_operator, "high_priority": high_priority})
    
    return response(success=True, message="Country operator added", status=201)

@routes.route('/country-operator/<country_operator>', methods=['DELETE'])
@jwt_required()
def delete_country_operator(country_operator):
    mongo_db = get_mongo_db()
    mongo_db.country_operators.delete_one({"country_operator": country_operator})
    return response(success=True, message="Country operator deleted", status=200)

# Start/Stop/Restart Program
@routes.route('/program/start', methods=['POST'])
@jwt_required()
def start_program():
    data = request.json
    session_name = f"program_{data['country_operator']}"
    return process_manager.start_program(session_name, data['phone_number'], data['proxy'])

@routes.route('/program/stop', methods=['POST'])
@jwt_required()
def stop_program():
    session_name = request.json.get('session_name')
    return process_manager.stop_program(session_name)

@routes.route('/program/restart', methods=['POST'])
@jwt_required()
def restart_program():
    data = request.json
    session_name = f"program_{data['country_operator']}"
    return process_manager.restart_program(session_name, data['phone_number'], data['proxy'])

# Get Program Status
@routes.route('/program/status', methods=['GET'])
@jwt_required()
def get_program_status():
    """Get the status of a program session."""
    session_name = request.args.get('session_name')

    if not session_name:
        return response(success=False, message="session_name parameter is required", status=400)

    status = process_manager.get_program_status(session_name)

    if status is not None:
        return response(success=True, data=status, status=200)
    
    return response(success=False, message="Session not found", status=404)

# Real-time Metrics with Pagination
@routes.route('/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    sms_sent = SMSSent.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return response(
        success=True, 
        data={
            "sms_sent": [sms.to_dict() for sms in sms_sent.items],
            "total": sms_sent.total,  # Include the total count of items
            "page": page,  # Current page number
            "per_page": per_page  # Items per page
        }, 
        status=200
    )

# Alerts
@routes.route('/alerts', methods=['POST'])
@jwt_required()
def send_alert_route():
    data = request.json
    message = data.get('message')
    
    if not message:
        return response(success=False, message="Message is required", status=400)
    
    # Send the message via the Telegram bot
    try:
        result = telegram_bot.send_message(message)
        
        if result is None:
            logging.error("Failed to send the Telegram alert.")
            return response(success=False, message="Failed to send alert. Check logs for more details.", status=500)
        
        logging.info("Alert sent successfully via Telegram.")
        return response(success=True, message="Alert sent successfully", status=200)
    
    except Exception as e:
        logging.error(f"Error sending alert: {str(e)}")
        return response(success=False, message=str(e), status=500)
