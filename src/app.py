"""
Manages the app creation and configuration process.
"""

import os

from flask import Flask

from .configs.flask import config as Config
from .db import db, migrate
from .views import telegram_bot_blueprint


def create_app(config_name: str = None) -> Flask:
    """
    Creates and configures the app.
    """
    app = Flask(__name__)

    configure_app(app, config_name)
    configure_db(app)
    configure_blueprints(app)

    return app


def configure_app(app: Flask, config_name: str):
    """
    Configures app.
    """
    if (not isinstance(config_name, str)):
        config_name = os.getenv("CONFIG_NAME", "default")

    config = Config[config_name]

    app.config.from_object(config)


def configure_db(app: Flask):
    """
    Configures database.
    """
    db.init_app(app)
    migrate.init_app(app, db)


def configure_blueprints(app: Flask):
    """
    Configures blueprints.
    """
    app.register_blueprint(
        telegram_bot_blueprint,
        url_prefix="/telegram_bot"
    )
