"""
Manages the app creation and configuration process.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import (
    Flask,
    redirect,
    url_for,
    current_app
)
from flask.logging import (
    default_handler as default_logging_handler
)

from .configs import flask_config
from .extensions import (
    db,
    migrate,
    redis_client,
    task_queue,
    babel
)
from .blueprints import (
    telegram_bot_blueprint,
    legal_blueprint
)
from .blueprints._common.utils import (
    absolute_url_for
)
# we need to import every model in order Migrate knows them
from .database.models import * # noqa: F403


def create_app(config_name: str = None) -> Flask:
    """
    Creates and configures the app.
    """
    if not isinstance(config_name, str):
        config_name = os.getenv("CONFIG_NAME", "default")

    app = Flask(__name__)

    configure_app(app, config_name)
    configure_logger(app)
    configure_extensions(app)
    configure_blueprints(app)
    configure_redirects(app)
    configure_error_handlers(app)

    app.logger.debug(
        f"App created and configured using {config_name} config"
    )

    return app


def configure_app(app: Flask, config_name: str) -> None:
    """
    Configures app.
    """
    config = flask_config[config_name]

    app.config.from_object(config)


def configure_logger(app: Flask) -> None:
    """
    Configures app logger.

    - should be called before any other configuration
    (except app configuration)
    """
    log_to_file = app.config["LOGGING_LOG_TO_FILE"]
    log_folder_name = app.config["LOGGING_LOG_FOLDER_NAME"]
    log_file_name = app.config["LOGGING_LOG_FILE_NAME"]
    log_file_max_bytes = app.config["LOGGING_LOG_FILE_MAX_BYTES"]
    log_file_backup_count = app.config["LOGGING_LOG_FILE_BACKUP_COUNT"]
    logging_level = app.config["LOGGING_LEVEL"]

    default_formatter_template = (
        "[{asctime}] [{levelname}] {module}: "
        "{message} ({pathname}:{lineno})",
    )
    debug_formatter_template = (
        "[{levelname}] {module}.{funcName}: {message}"
    )
    runtime_formatter_template = (
        debug_formatter_template if
        (logging_level == logging.DEBUG) else
        default_formatter_template
    )

    handlers = []

    if log_to_file:
        os.makedirs(log_folder_name, exist_ok=True)

        file_handler = RotatingFileHandler(
            encoding="utf-8",
            filename=os.path.join(
                log_folder_name,
                log_file_name
            ),
            maxBytes=log_file_max_bytes,
            backupCount=log_file_backup_count
        )
        formatter = logging.Formatter(
            runtime_formatter_template,
            style="{",
            validate=True
        )

        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    else:
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            runtime_formatter_template,
            style="{",
            validate=True
        )

        stream_handler.setFormatter(formatter)
        handlers.append(stream_handler)

    app.logger.removeHandler(default_logging_handler)

    for handler in handlers:
        handler.setLevel(logging_level)
        app.logger.addHandler(handler)

    app.logger.setLevel(logging_level)


def configure_extensions(app: Flask) -> None:
    """
    Configures Flask extensions.
    """
    # Database
    db.init_app(app)

    # Migration
    migrate.init_app(app, db)

    # i18n
    babel.init_app(app)

    # Redis
    redis_client.init_app(app)

    # RQ
    if redis_client.is_enabled:
        task_queue.init_app(app, redis_client.connection)


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
