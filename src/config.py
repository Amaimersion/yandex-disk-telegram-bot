"""
Configurations of the app for specific environments.
"""

import os

from dotenv import load_dotenv


load_dotenv(verbose=True)


class Config:
    # Flask
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")


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
