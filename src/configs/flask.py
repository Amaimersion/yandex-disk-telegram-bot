"""
Configurations of the Flask app for specific environments.
"""

import os
from enum import Enum, auto

from dotenv import load_dotenv


def load_env():
    config_name = os.getenv("CONFIG_NAME")
    file_names = {
        "production": ".env.production",
        "development": ".env.development",
        "testing": ".env.testing"
    }
    file_name = file_names.get(config_name)

    if file_name is None:
        raise Exception(
            "Unable to map configuration name and .env.* files. "
            "Did you forget to set env variables?"
        )

    load_dotenv(file_name)


load_env()


class YandexOAuthAPIMethod(Enum):
    """
    Which method to use for Yandex OAuth API.
    """
    # When user give access, he will be redirected
    # to the app site, and app will extract code
    # automatically.
    # https://yandex.ru/dev/oauth/doc/dg/reference/auto-code-client.html
    AUTO_CODE_CLIENT = auto()

    # When user give access, he will see code, and
    # that code user should manually send to the Telegram bot.
    # This method intended for cases when you don't have
    # permanent domain name (for example, when testing with `ngrok`)
    # or when you want to hide it.
    # `AUTO_CODE_CLIENT` provides better UX.
    # https://yandex.ru/dev/oauth/doc/dg/reference/console-client.html/
    CONSOLE_CLIENT = auto()


class Config:
    """
    Notes:
    - don't remove any keys from this configuration, because code
    logic can depend on this. Instead, set "off" value (if code logic
    supports it); or set empty value and edit code logic to handle
    such values.
    - keep in mind that Telegram, Heroku, etc. have request timeout.
    It is about 30 seconds, but actual value can be different.
    If you don't end current request in a long time, then it will
    be force closed. Telegram will send new request in that case.
    Try to always use background task queue, not block current thread.
    If you have no opportunity to use background task queue, then
    change current configuration in order request with blocked thread
    will be not able to take long time to complete.
    """
    # region Project

    # name of app that will be used in HTML and so on
    PROJECT_APP_NAME = "Yandex.Disk Telegram Bot"
    PROJECT_AUTHOR = "Sergey Kuznetsov"
    PROJECT_URL_FOR_CODE = "https://github.com/Amaimersion/yandex-disk-telegram-bot" # noqa
    PROJECT_URL_FOR_ISSUE = "https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/new?template=bug_report.md" # noqa
    PROJECT_URL_FOR_REQUEST = "https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/new?template=feature_request.md" # noqa
    PROJECT_URL_FOR_QUESTION = "https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/new?template=question.md" # noqa
    PROJECT_URL_FOR_BOT = "https://t.me/Ya_Disk_Bot"

    # endregion

    # region Runtime (interaction of bot with user, behavior of bot, etc.)

    # Default value (in seconds) when setted but unused
    # disposable handler should expire and be removed.
    # Example: user send `/create_folder` but didn't send
    # any data for that command; bot will handle next message
    # as needed data for that command; if user don't send any
    # data in 10 minutes, then this handler will be removed from queue.
    # Keep in mind that it is only recommended default value,
    # specific handler can use it own expiration time and ignore
    # this value at all.
    # Set to 0 to disable expiration
    RUNTIME_DISPOSABLE_HANDLER_EXPIRE = 60 * 10

    # Dispatcher will bind command to message date.
    # How long this data should be stored. In seconds.
    # We don't need to memorize it for a long, because
    # bot expects messages with exact same date to be sent
    # in a short period of time (for example, "Forward" sents
    # messages one by one as fast as server process them;
    # or user uploads all files as media group within 1 minute).
    RUNTIME_SAME_DATE_COMMAND_EXPIRE = 60 * 2

    # RQ (background tasks queue) is enabled.
    # Also depends on `REDIS_URL`
    RUNTIME_RQ_ENABLED = True

    # Maximum runtime of uploading process in `/upload`
    # before it’s interrupted. In seconds.
    # This value shouldn't be less than
    # `YANDEX_DISK_API_CHECK_OPERATION_STATUS_MAX_ATTEMPTS` *
    # `YANDEX_DISK_API_CHECK_OPERATION_STATUS_INTERVAL`.
    # This timeout should be used only for force quit if
    # uploading function start behave incorrectly.
    # Use `MAX_ATTEMPTS` and `INTERVAL` for expected quit.
    # Applied only if task queue (RQ, for example) is enabled
    RUNTIME_UPLOAD_WORKER_JOB_TIMEOUT = 30

    # Maximum queued time of upload function before it's discarded.
    # "Queued" means function awaits execution.
    # In seconds. `None` for infinite awaiting.
    # Applied only if task queue (RQ, for example) is enabled
    RUNTIME_UPLOAD_WORKER_UPLOAD_TTL = None

    # How long successful result of uploading is kept.
    # In seconds.
    # Applied only if task queue (RQ, for example) is enabled
    RUNTIME_UPLOAD_WORKER_RESULT_TTL = 0

    # How long failed result of uploading is kept.
    # "Failed result" means function raises an error,
    # not any logical error returns from function.
    # In seconds.
    # Applied only if task queue (RQ, for example) is enabled
    RUNTIME_UPLOAD_WORKER_FAILURE_TTL = 0

    # See `RUNTIME_UPLOAD_WORKER_JOB_TIMEOUT` documentation.
    # This value is for `/element_info` worker.
    RUNTIME_ELEMENT_INFO_WORKER_JOB_TIMEOUT = 5

    # See `RUNTIME_UPLOAD_WORKER_UPLOAD_TTL` documentation.
    # This value is for `/element_info` worker.
    # Because worker is used only to send preview,
    # we will use small TTL, because if all workers
    # are busy, most likely it can take a long time
    # before preview will be sended. There is no point
    # to send preview after 5 minutes - preview should
    # be sended either now or never.
    RUNTIME_ELEMENT_INFO_WORKER_TTL = 10

    # See `RUNTIME_UPLOAD_WORKER_JOB_TIMEOUT` documentation.
    # This value is for `/space_info` worker.
    RUNTIME_SPACE_INFO_WORKER_TIMEOUT = 5

    # After what time `/settings` handler should forget
    # about user last action.
    # For example, user called `/settings` command, then
    # clicked on "Change default upload folder" button.
    # Bot will wait for next message (new folder name) and
    # store some additional data (last action of that user).
    # If user not sent any message in N seconds, then bot
    # will clear all data about user last action and user
    # have to click again on "Change default upload folder" button.
    # In seconds.
    # Set to 0 to disable expiration.
    # Applied only if Redis is enabled
    RUNTIME_SETTINGS_LAST_ACTION_EXPIRE = 60 * 60 * 24 * 1

    # endregion

    # region Flask

    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # endregion

    # region Flask SQLAlchemy

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///temp.sqlite"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # endregion

    # region Babel

    BABEL_DEFAULT_LOCALE = "en"
    BABEL_TRANSLATION_DIRECTORIES = "../translations"

    # endregion

    # region Redis

    REDIS_URL = os.getenv("REDIS_URL")

    # endregion

    # region Telegram API

    # postfix of original webhook route.
    # For example, original route is `/webhook`,
    # and postfix is `_akdb2v`, final route that will
    # be used is `/webhook_akdb2v`.
    # You will need to set this address as webhook URL.
    # It is intended for security reasons.
    # WARNING: use env variable to set this value,
    # don't use this app config to set it. It is because
    # value will be read directly from env variable,
    # and app config will not have any effect.
    TELEGRAM_API_WEBHOOK_URL_POSTFIX = os.getenv(
        "TELEGRAM_API_WEBHOOK_URL_POSTFIX",
        ""
    )

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

    # endregion

    # region Yandex OAuth API

    # stop waiting for a Yandex response
    # after a given number of seconds
    YANDEX_OAUTH_API_TIMEOUT = 15

    # see `YandexOAuthAPIMethod` for more
    YANDEX_OAUTH_API_METHOD = YandexOAuthAPIMethod.AUTO_CODE_CLIENT

    # `insert_token` (controls `INSERT` operation)
    # will contain N random bytes. Each byte will be
    # converted to two hex digits
    YANDEX_OAUTH_API_INSERT_TOKEN_BYTES = 8

    # lifetime of `insert_token` in seconds starting
    # from date of issue. It is better to find
    # best combination between `bytes` and `lifetime`
    YANDEX_OAUTH_API_INSERT_TOKEN_LIFETIME = 60 * 10

    # endregion

    # region Yandex.Disk API

    # stop waiting for a Yandex response
    # after a given number of seconds
    YANDEX_DISK_API_TIMEOUT = 5

    # maximum number of checks of operation status
    # (for example, if file is downloaded by Yandex.Disk).
    # It is blocks request until check ending!
    YANDEX_DISK_API_CHECK_OPERATION_STATUS_MAX_ATTEMPTS = 5

    # interval in seconds between checks of operation status.
    # It is blocks request until check ending!
    # For example, if max. attempts is 5 and interval is 2,
    # then request will be blocked maximum for (5 * 2) seconds.
    YANDEX_DISK_API_CHECK_OPERATION_STATUS_INTERVAL = 2

    # endregion

    # region Google Analytics

    GOOGLE_ANALYTICS_UA = os.getenv("GOOGLE_ANALYTICS_UA")

    # endregion


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
    YANDEX_OAUTH_API_METHOD = YandexOAuthAPIMethod.CONSOLE_CLIENT


class TestingConfig(Config):
    DEBUG = False
    TESTING = True


config = {
    "default": ProductionConfig,
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig
}
