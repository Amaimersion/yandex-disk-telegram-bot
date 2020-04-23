"""
Manages the app creation and configuration process.
"""

import os

from flask import (
    Flask,
    redirect,
    url_for
)

from .configs import flask_config
from .database import db, migrate
from .blueprints import telegram_bot_blueprint


def create_app(config_name: str = None) -> Flask:
    """
    Creates and configures the app.
    """
    app = Flask(__name__)

    configure_app(app, config_name)
    configure_db(app)
    configure_blueprints(app)
    configure_redirects(app)

    return app


def configure_app(app: Flask, config_name: str = None) -> None:
    """
    Configures app.
    """
    if (not isinstance(config_name, str)):
        config_name = os.getenv("CONFIG_NAME", "default")

    config = flask_config[config_name]

    app.config.from_object(config)


def configure_db(app: Flask) -> None:
    """
    Configures database.
    """
    db.init_app(app)
    migrate.init_app(app, db)


def configure_blueprints(app: Flask) -> None:
    """
    Configures blueprints.
    """
    app.register_blueprint(
        telegram_bot_blueprint,
        url_prefix="/telegram_bot"
    )


def configure_redirects(app: Flask) -> None:
    """
    Configures redirects.
    """
    @app.route("/favicon.ico")
    def favicon():
        return redirect(
            url_for(
                "static",
                filename="favicons/favicon.ico"
            )
        )
