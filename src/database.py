"""
This module defines the database models for a Flask application. 
It includes two models: User and Bookmark.
"""

from flask_sqlalchemy import SQLAlchemy
from enum import unique
from datetime import datetime
import string
import random

# Initialize the SQLAlchemy database instance
db = SQLAlchemy()

class User(db.Model):
    """
    A class that defines the User model.

    Attributes:
        id (int): The primary key of the User table.
        username (str): The username of the user, must be unique.
        email (str): The email address of the user, must be unique.
        password (str): The hashed password of the user.
        created_at (datetime): The timestamp when the user was created.
        updated_at (datetime): The timestamp when the user was last updated.
        bookmarks (relationship): A relationship to the Bookmark model.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    bookmarks = db.relationship("Bookmark", backref="user")

    def __repr__(self) -> str:
        """
        Provides a string representation of the User instance.

        Returns:
            str: A formatted string with the username.
        """
        return f"User>>> {self.username}"


class Bookmark(db.Model):
    """
    A class that defines the Bookmark model.

    Attributes:
        id (int): The primary key of the Bookmark table.
        body (str): An optional description of the bookmark.
        url (str): The full URL of the bookmark.
        short_url (str): A shortened version of the URL, defaults to 3 random characters.
        visit (int): The number of times the bookmark has been visited.
        user_id (int): A foreign key linking the bookmark to a user.
        created_at (datetime): The timestamp when the bookmark was created.
        updated_at (datetime): The timestamp when the bookmark was last updated.
    """

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=True)
    visit = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def generate_short_char(self):
        """
        Generates a unique short URL consisting of 3 random alphanumeric characters.

        Returns:
            str: A unique 3-character string for the short URL.
        """
        chars = string.digits + string.ascii_letters
        picked_chars = "".join(random.choices(chars, k=3))

        link = self.query.filter_by(short_url=picked_chars).first()

        if link:
            self.generate_short_char()
        else:
            return picked_chars

    def __init__(self, **kwargs):
        """
        Initializes the Bookmark instance and assigns a unique short URL.

        Args:
            **kwargs: Arbitrary keyword arguments for Bookmark attributes.
        """
        super().__init__(**kwargs)
        self.short_url = self.generate_short_char()

    def __repr__(self) -> str:
        """
        Provides a string representation of the Bookmark instance.

        Returns:
            str: A formatted string with the URL.
        """
        return f"Bookmark>>> {self.url}"