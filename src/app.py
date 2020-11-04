"""
Manages the app creation and configuration process.
"""

import os
from typing import (
    Union
)

from flask import (
    Flask,
    redirect,
    url_for,
    current_app
)
import redis

from .configs import flask_config
from .database import db, migrate
from .blueprints import (
    telegram_bot_blueprint,
    legal_blueprint
)
from .blueprints.utils import (
    absolute_url_for
)


# `None` means Redis not enabled
redis_client: Union[redis.Redis, None] = None


def create_app(config_name: str = None) -> Flask:
    """
    Creates and configures the app.
    """
    app = Flask(__name__)

    configure_app(app, config_name)
    configure_db(app)
    configure_blueprints(app)
    configure_redirects(app)
    configure_error_handlers(app)
    configure_redis(app)

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
    app.register_blueprint(
        legal_blueprint,
        url_prefix="/legal"
    )


def configure_redirects(app: Flask) -> None:
    """
    Configures redirects.

    Note: all redirects to static content should be handled by
    HTTP Reverse Proxy Server, not by WSGI HTTP Server.
    We are keeping this redirect to static favicon only for
    development builds where usually only Flask itself is used
    (we want to see favicon at development stage - it is only the reason).
    """
    @app.route("/favicon.ico")
    def favicon():
        return redirect(
            absolute_url_for(
                "static",
                filename="favicons/favicon.ico"
            )
        )


def configure_error_handlers(app: Flask) -> None:
    """
    Configures error handlers.
    """
    if not app.config["DEBUG"]:
        @app.errorhandler(404)
        def not_found(error):
            """
            We will redirect all requests rather than send "Not Found"
            error, because we using web pages only for exceptional cases.
            It is expected that all interaction with user should go
            through Telegram when possible.
            """
            return redirect(
                location=app.config["PROJECT_URL_FOR_BOT"],
                # temporary, in case if some routes will be added in future
                code=302
            )


def configure_redis(app: Flask) -> None:
    global redis_client

    redis_server_url = app.config["REDIS_URL"]

    if not redis_server_url:
        return

    redis_client = redis.from_url(
        redis_server_url,
        decode_responses=True
    )
