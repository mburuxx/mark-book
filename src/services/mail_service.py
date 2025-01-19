"""
This module provides functionality for sending emails asynchronously 
using Flask-Mail and threading. It includes support for both plain-text 
and HTML email content.
"""

from http.client import INTERNAL_SERVER_ERROR
from threading import Thread
from flask_mail import Message
from app import app
from app import mail


def send_async_email(app, msg):
    """
    Sends an email asynchronously within the Flask app context.

    Args:
        app (Flask): The Flask application instance.
        msg (Message): The email message to send.

    Raises:
        INTERNAL_SERVER_ERROR: Raised when the mail server connection fails.
    """
    with app.app_context():
        try:
            mail.send(msg)
        except ConnectionRefusedError:
            raise INTERNAL_SERVER_ERROR("[MAIL SERVER] not working")


def send_email(subject, sender, recipients, text_body, html_body):
    """
    Prepares and sends an email asynchronously.

    Args:
        subject (str): The subject of the email.
        sender (str): The sender's email address.
        recipients (list): A list of recipient email addresses.
        text_body (str): The plain-text version of the email body.
        html_body (str): The HTML version of the email body.

    Returns:
        None: The email is sent asynchronously in a separate thread.
    """
    # Create a new email message
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    # Send the email in a new thread
    Thread(target=send_async_email, args=(app, msg)).start()