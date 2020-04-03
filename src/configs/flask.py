"""
Configurations of the Flask app for specific environments.
"""

import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    # Flask
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Telegram API
    # stop waiting for a Telegram response
    # after a given number of seconds
    TELEGRAM_API_TIMEOUT = 5

    # Yandex Oauth API
    # stop waiting for a Yandex response
    # after a given number of seconds
    YANDEX_OAUTH_API_TIMEOUT = 30

    # Yandex.Disk API
    # `insert_token` (controls `INSERT` operation)
    # will contain n random bytes. Each byte will be
    # converted to two hex digits
    YANDEX_DISK_API_INSERT_TOKEN_BYTES = 8
    # lifetime of `insert_token` in seconds starting
    # from date of issue. It is better to find
    # best combination between `bytes` and `lifetime`
    YANDEX_DISK_API_INSERT_TOKEN_LIFETIME = 60 * 10

    # Project
    # name of app that will be used in HTML and so on
    PROJECT_APP_NAME = "Yandex.Disk Bot"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    USE_X_SENDFILE = True
    PREFERRED_URL_SCHEME = "HTTPS"


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SECRET_KEY = "q8bjscr0sLmAf50gXRFaIghoS7BvDd4Afxo2RjT3r3E="
    SQLALCHEMY_DATABASE_URI = "sqlite:///development.sqlite"
    SQLALCHEMY_ECHO = "debug"


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SECRET_KEY = "ReHdIY8zGRQUJRTgxo_zeKiv3MjIU-OYBD66GlW9ZKw="
    SQLALCHEMY_DATABASE_URI = "sqlite:///testing.sqlite"


config = {
    "default": ProductionConfig,
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig
}
