#!/usr/bin/python3
"""
This module contains the authentication routes for user registration and user details retrieval.
It defines a Flask Blueprint for user authentication-related operations.
"""

from flask import Blueprint, request, jsonify
import validators
from werkzeug.security import check_password_hash, generate_password_hash
from src.constants.http_status_code import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from src.database import User, db

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

@auth.get("/me")
def me():
    """
    Retrieves the details of the currently authenticated user.

    This route can be used to fetch the current user's profile information.

    Returns:
        Response: A JSON response with a placeholder message. In a real application, it should return
        actual user details from the database.
    """
    return {"user": "me"}
