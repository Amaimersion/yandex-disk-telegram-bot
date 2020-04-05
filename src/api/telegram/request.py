import os

import requests
from flask import current_app

from .exceptions import (
    InvalidResponseFormatException,
    MethodExecutionFailedException
)


def create_url(method_name: str) -> str:
    """
    Creates Telegram Bot API URL for calling.

    :param method_name: Name of API method in URL.
    """
    bot_token = os.getenv("TELEGRAM_API_BOT_TOKEN", "")
    base_url = "https://api.telegram.org"
    bot_url = "bot{token}".format(token=bot_token)
    url = f"{base_url}/{bot_url}/{method_name}"

    return url


def create_file_download_url(file_path: str) -> str:
    """
    :param file_path: `file_path` property of `File` object.

    :returns: URL for downloading of Telegram file.
    """
    bot_token = os.getenv("TELEGRAM_API_BOT_TOKEN", "")
    base_url = "https://api.telegram.org/file"
    bot_url = "bot{token}".format(token=bot_token)
    url = f"{base_url}/{bot_url}/{file_path}"

    return url


def make_request(method_name: str, data: dict) -> dict:
    """
    Makes HTTP request to Telegram API.

    :param method_name: Name of API method in URL.
    :param data: JSON data to send.

    :returns: Response data from Telegram.

    :raises requests.RequestException:
    https://requests.readthedocs.io/en/master/api/#exceptions
    :raises TelegramApiException:
    See `exceptions.py` for documentation.
    """
    timeout = current_app.config.get("TELEGRAM_API_TIMEOUT", 5)
    url = create_url(method_name)
    response = requests.post(
        url,
        json=data,
        timeout=timeout,
        allow_redirects=False,
        verify=True
    )

    response.raise_for_status()

    response_data = {}

    try:
        response_data = response.json()
    except ValueError:
        raise InvalidResponseFormatException("Not a JSON response")

    ok = response_data.get("ok")

    if (ok is None):
        raise InvalidResponseFormatException('Response without "ok" key')

    if (not ok):
        error_code = response_data.get("error_code", "?")
        description = response_data.get("description", "?")
        message = f"{method_name} failed with {error_code} ({description})"

        raise MethodExecutionFailedException(message)

    return response_data["result"]
