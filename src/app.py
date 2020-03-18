"""
Manages the app creation and configuration process.
"""

import os

from flask import Flask

from .configs.flask import config as Config


def create_app(config_name=None):
    """Creates and configures the app."""
    app = Flask(__name__)

    configure_app(app, config_name)

    @app.route("/")
    def index():
        return "Hello!"

    return app


def configure_app(app, config_name):
    if (not isinstance(config_name, str)):
        config_name = os.getenv("CONFIG_NAME", "default")

    config = Config[config_name]

    app.config.from_object(config)
