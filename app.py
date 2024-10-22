from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token
from models import mongo_db, get_sms_metrics
from sms_program_manager import start_program, stop_program, restart_program
from utils import rate_limit
from telegram_bot import send_telegram_alert
from config import Config

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY

jwt = JWTManager(app)

# Authentication Route
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if username == "admin" and password == "password":
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

# Route to control programs
@app.route('/program/<string:action>', methods=['POST'])
def control_program(action):
    session_name = request.json.get('session_name')

    if action == "start":
        start_program(session_name)
        return jsonify({"msg": "Program started"}), 200
    elif action == "stop":
        stop_program(session_name)
        return jsonify({"msg": "Program stopped"}), 200
    elif action == "restart":
        restart_program(session_name)
        return jsonify({"msg": "Program restarted"}), 200
    else:
        return jsonify({"msg": "Invalid action"}), 400

# Route to get SMS metrics
@app.route('/metrics', methods=['GET'])
def get_metrics():
    metrics = get_sms_metrics()
    return jsonify(metrics), 200

# Route for rate limiting
@app.route('/send_sms', methods=['POST'])
def send_sms():
    country = request.json.get('country')
    if rate_limit(country):
        return jsonify({"msg": "SMS sent successfully"}), 200
    else:
        return jsonify({"msg": "Rate limit exceeded"}), 429

# Route to send an alert
@app.route('/alert', methods=['POST'])
def alert():
    message = request.json.get('message')
    send_telegram_alert(message)
    return jsonify({"msg": "Alert sent"}), 200

if __name__ == '__main__':
    app.run(debug=True)