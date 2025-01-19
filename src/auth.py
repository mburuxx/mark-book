"""
This module contains the authentication routes for user registration and user details retrieval.
It defines a Flask Blueprint for user authentication-related operations.
"""

from flask import Blueprint, request, jsonify
import validators
from werkzeug.security import check_password_hash, generate_password_hash
from src.constants.http_status_code import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from src.database import User, db
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, create_refresh_token

# Create a Blueprint for authentication routes
auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/v1/auth"
)

@auth.post("/register")
def register():
    """
    Registers a new user.

    This route accepts a JSON payload with 'username', 'email', and 'password', performs
    validation, and creates a new user in the database if all checks pass.

    Returns:
        Response: A JSON response with a message indicating success or an error, along with an HTTP status code.
    """
    # Extract user details from the request
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    # Validate the length of the password
    if len(password) < 6:
        return jsonify({"error": "Password is too short!"}), HTTP_400_BAD_REQUEST

    # Validate the length of the username
    if len(username) < 4:
        return jsonify({"error": "Username is too short!"}), HTTP_400_BAD_REQUEST

    # Validate the email format
    if not validators.email(email):
        return jsonify({"error": "Please enter a valid email address"}), HTTP_400_BAD_REQUEST

    # Check if the email is already taken
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "This email is already taken!"}), HTTP_409_CONFLICT
    
    # Check if the username is already taken
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"error": "This username is already taken!"}), HTTP_409_CONFLICT

    # Hash the user's password
    pwd_hash = generate_password_hash(password)

    # Create a new user instance
    user = User(username=username, password=pwd_hash, email=email)
    
    # Add the user to the session and commit to the database
    db.session.add(user)
    db.session.commit()
    
    # Return a success message and user details
    return jsonify({
        "message": "User successfully created",
        "user": {
            "username": username,
            "email": email
        }
    }), HTTP_201_CREATED

@auth.post("/login")
def login():
    """
    Logs in an existing user.

    This route accepts a JSON payload with 'email' and 'password', verifies the credentials,
    and generates JWT tokens for the user if the login is successful.

    Returns:
        Response: A JSON response containing access and refresh tokens, user details, 
        or an error message with the appropriate HTTP status code.
    """
    # Extract email and password from the request
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    # Retrieve the user by email from the database
    user = User.query.filter_by(email=email).first()

    # Check if the user exists
    if user:
        # Verify if the provided password matches the stored password hash
        is_pass_correct = check_password_hash(user.password, password)
        if is_pass_correct:
            # Generate JWT tokens for the user (access and refresh tokens)
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            # Return a response with the tokens and user details
            return jsonify({
                "user": {
                    "refresh": refresh,
                    "access": access,
                    "username": user.username,
                    "email": user.email
                }
            }), HTTP_200_OK
        
    # If user not found or credentials are incorrect, return an error message
    return jsonify({"error": "Wrong credentials!"}), HTTP_401_UNAUTHORIZED

@auth.get("/me")
@jwt_required()
def me():
    """
    Retrieves the details of the currently authenticated user.

    This route can be used to fetch the current user's profile information.

    Returns:
        Response: A JSON response with actual user details from the database.
    """
    user_id = get_jwt_identity()

    user = User.query.filter_by(id=user_id).first()

    return  jsonify({
        "username": user.username,
        "email": user.email
        }), HTTP_200_OK

@auth.post('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()

    access = create_access_token(identity=identity)

    return jsonify({
        'access' : access
    }), HTTP_200_OK