"""
Configurations of the Flask app for specific environments.
"""

import os

from dotenv import load_dotenv


load_dotenv(verbose=True)


class Config:
    # Flask settings
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # Telegram settings
    TELEGRAM_BOT_API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


config = {
    "default": ProductionConfig,
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig
}
