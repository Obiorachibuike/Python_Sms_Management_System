from flask_jwt_extended import create_access_token
from models import User  # Assuming your User model is in models.py
import bcrypt

class Auth:
    def authenticate(self, email, password):
        # Check if user exists in the database using email
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return user  # Return the user object if authentication is successful
        return None  # Return None if authentication fails

    def create_access_token(self, user):
        # Create an access token using the user's identity (email)
        return create_access_token(identity=user.email)
