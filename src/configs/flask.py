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
    # stop waiting for a Telegram response after a given number of seconds
    TELEGRAM_API_TIMEOUT = 5


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


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
