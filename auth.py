from flask_jwt_extended import create_access_token
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# Sample user database
users = {"admin": generate_password_hash("password")}

def login_user():
    # Get username and password from the request
    username = request.json.get('username')
    password = request.json.get('password')
    
    # Check if the username exists and if the password is correct
    if username in users and check_password_hash(users[username], password):
        # Create an access token for the authenticated user
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    
    # Return an error message if authentication fails
    return jsonify({"msg": "Bad username or password"}), 401
