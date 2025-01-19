"""
This module defines the main Flask application factory function (`create_app`) 
and configures the application with its routes, extensions, and error handlers.
"""

import os
from flask import Flask, redirect, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger, swag_from
from src.bookmarks import bookmarks
from src.auth import auth
from config.swagger import swagger_config, template
from src.database import db, Bookmark
from src.constants.http_status_code import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND


def create_app(test_config=None):
    """
    Application factory for creating and configuring the Flask app.

    Args:
        test_config (dict, optional): Configuration dictionary for testing purposes. 
                                       Defaults to None.

    Returns:
        Flask: Configured Flask application instance.
    """
    # Initialize the Flask app
    app = Flask(__name__, instance_relative_config=True)

    # Load default or testing configuration
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY="dev",
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),
            SWAGGER={
                "title": "Bookmarks API",
                "uiversion": 3,
            },
        )
    else:
        app.config.from_mapping(test_config)

    # Initialize JWT Manager
    JWTManager(app)

    # Enable Cross-Origin Resource Sharing (CORS)
    CORS(app)

    # Initialize database with app context
    db.app = app
    db.init_app(app)

    # Set up Swagger for API documentation
    Swagger(app, config=swagger_config, template=template)

    # Register application blueprints
    app.register_blueprint(bookmarks)
    app.register_blueprint(auth)

    @app.route("/<short_url>")
    @swag_from("./docs/bookmarks/redirect.yml")
    def redirect_to_url(short_url):
        """
        Redirects to the full URL associated with the given short URL.

        Args:
            short_url (str): The short URL key to look up.

        Returns:
            Response: A redirect to the corresponding full URL.

        Raises:
            404 Error: If the short URL does not exist.
        """
        link = Bookmark.query.filter_by(short_url=short_url).first_or_404()
        link.visits += 1
        db.session.commit()
        return redirect(link.url)

    @app.errorhandler(404)
    def page_not_found(e):
        """
        Handles 404 errors.

        Args:
            e: The error object.

        Returns:
            JSON: A response with an error message and a 404 status code.
        """
        return jsonify({"Error": "Not found"}), HTTP_404_NOT_FOUND

    @app.errorhandler(500)
    def server_error(e):
        """
        Handles 500 errors.

        Args:
            e: The error object.

        Returns:
            JSON: A response with an error message and a 500 status code.
        """
        return jsonify({"Error": "Issue on server occurred"}), HTTP_500_INTERNAL_SERVER_ERROR

    return app