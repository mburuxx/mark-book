"""
This module defines the authentication routes for a Flask application.
It handles user registration, login, and token refresh functionality.
"""

from flask import Blueprint, request, jsonify, redirect
from src.database import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, create_refresh_token, get_jwt_identity
from flasgger import swag_from
import validators
from src.constants.http_status_code import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
    HTTP_400_BAD_REQUEST,
)

# Initialize the Blueprint for authentication routes
auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post("/signup")
@swag_from("./docs/auth/register.yml")
def create_user():
    """
    Handles user registration.

    Validates the user input, checks for duplicate usernames or emails,
    and creates a new user in the database.

    Returns:
        JSON response with user details on success or error messages on failure.
    """
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]
    pw_hash = generate_password_hash(password)

    if len(password) < 6:
        return jsonify({"password": ["Passwords should be at least 6 characters long"]}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({"username": ["Usernames should be at least 3 characters long"]}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({"email": ["Email is of invalid format"]}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({"username": ["Username should only contain alphanumeric characters, no spaces"]}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"email": ["Email is already taken"]}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"username": ["Username is already taken"]}), HTTP_409_CONFLICT

    user = User(username=username, email=email, password=pw_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify(
        {
            "user": {
                "username": username,
                "email": email,
            }
        }
    ), HTTP_201_CREATED


@auth.post("/login")
@swag_from("./docs/auth/login.yml")
def login():
    """
    Handles user login.

    Validates user credentials and returns access and refresh tokens
    on successful authentication.

    Returns:
        JSON response with user details and tokens on success or an error message on failure.
    """
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    user = User.query.filter_by(email=email).first()

    if user:
        pass_correct = check_password_hash(user.password, password)
        if pass_correct:
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return jsonify(
                {
                    "user": {
                        "username": user.username,
                        "email": user.email,
                        "token": access_token,
                        "refresh_token": refresh_token,
                    }
                }
            ), HTTP_200_OK

    return jsonify({"message": "Invalid credentials"}), HTTP_401_UNAUTHORIZED


@auth.post("/token/refresh")
@jwt_required(refresh=True)
@swag_from("./docs/auth/refresh_token.yml")
def refresh():
    """
    Handles token refresh.

    Generates a new access token using a valid refresh token.

    Returns:
        JSON response with a new access token.
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), HTTP_200_OK