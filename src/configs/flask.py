"""
Configurations of the Flask app for specific environments.
"""

import os

from dotenv import load_dotenv


def load_env():
    config_name = os.getenv("CONFIG_NAME")
    file_names = {
        "production": ".env.production",
        "development": ".env.development",
        "testing": ".env.testing"
    }
    file_name = file_names.get(config_name)

    if (file_name is None):
        raise Exception(
            "Unable to map configuration name "
            "and .env.* files"
        )

    load_dotenv(file_name)


load_env()


class Config:
    """
    Notes:
    - keep in mind that Heroku have 30 seconds request timeout.
    So, if your configuration value can exceed 30 seconds, then
    request will be terminated by Heroku.
    """
    # Project
    # name of app that will be used in HTML and so on
    PROJECT_APP_NAME = "Yandex.Disk Telegram Bot"
    PROJECT_AUTHOR = "Sergey Kuznetsov"
    PROJECT_URL_FOR_CODE = "https://github.com/Amaimersion/yandex-disk-telegram-bot" # noqa
    PROJECT_URL_FOR_ISSUE = "https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/new?template=bug_report.md" # noqa
    PROJECT_URL_FOR_REQUEST = "https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/new?template=feature_request.md" # noqa
    PROJECT_URL_FOR_QUESTION = "https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/new?template=question.md" # noqa
    PROJECT_URL_FOR_BOT = "https://t.me/Ya_Disk_Bot"

    # Flask
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # Flask SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///temp.sqlite"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_URL = os.getenv("REDIS_URL")

    # Telegram API
    # stop waiting for a Telegram response
    # after a given number of seconds
    TELEGRAM_API_TIMEOUT = 5
    # maximum file size in bytes that bot
    # can handle by itself.
    # It is Telegram limit, not bot.
    # Binary system should be used, not decimal.
    # For example, MebiBytes (M = 1024 * 1024),
    # not MegaBytes (MB = 1000 * 1000).
    # In Linux you can use `truncate -s 20480K test.txt`
    # to create exactly 20M file
    TELEGRAM_API_MAX_FILE_SIZE = 20 * 1024 * 1024

    # Yandex OAuth API
    # stop waiting for a Yandex response
    # after a given number of seconds
    YANDEX_OAUTH_API_TIMEOUT = 15

    # Yandex.Disk API
    # stop waiting for a Yandex response
    # after a given number of seconds
    YANDEX_DISK_API_TIMEOUT = 5
    # `insert_token` (controls `INSERT` operation)
    # will contain n random bytes. Each byte will be
    # converted to two hex digits
    YANDEX_DISK_API_INSERT_TOKEN_BYTES = 8
    # lifetime of `insert_token` in seconds starting
    # from date of issue. It is better to find
    # best combination between `bytes` and `lifetime`
    YANDEX_DISK_API_INSERT_TOKEN_LIFETIME = 60 * 10
    # maximum number of checks of operation status
    # (for example, if file is downloaded by Yandex.Disk).
    # It is blocks request until check ending!
    YANDEX_DISK_API_CHECK_OPERATION_STATUS_MAX_ATTEMPTS = 5
    # interval in seconds between checks of operation status.
    # It is blocks request until check ending!
    # For example, if max. attempts is 5 and interval is 2,
    # then request will be blocked maximum for (5 * 2) seconds.
    YANDEX_DISK_API_CHECK_OPERATION_STATUS_INTERVAL = 2
    # in this folder files will be uploaded by default
    # if user not specified custom folder.
    YANDEX_DISK_API_DEFAULT_UPLOAD_FOLDER = "Telegram Bot"

    # Google Analytics
    GOOGLE_ANALYTICS_UA = os.getenv("GOOGLE_ANALYTICS_UA")


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    USE_X_SENDFILE = True
    SERVER_NAME = os.getenv("SERVER_NAME")
    PREFERRED_URL_SCHEME = "https"


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = "debug"


class TestingConfig(Config):
    DEBUG = False
    TESTING = True


config = {
    "default": ProductionConfig,
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig
}
