from flask import Flask
import os

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRWT_KEY = os.environ.get("SECRET_KEY")
        )

    else:
        app.config.from_mapping(test_config)

    @app.get("/")

    def index():
        return "Welcome Home Again!"

    @app.get("/hello")
    def say_hello():
        return {"message" : "Hello Developer!"}

    return app