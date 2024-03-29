from os import environ

from flask import current_app

from src.http.request import (
    create_url,
    request
)
from .exceptions import (
    RequestFailed
)


def create_bot_url(method_name: str) -> str:
    """
    Creates Telegram Bot API URL for request.

    :param method_name: Name of API method in URL.
    """
    token = environ["TELEGRAM_API_BOT_TOKEN"]

    return create_url(
        "https://api.telegram.org",
        f"bot{token}",
        method_name
    )


def create_file_download_url(file_path: str) -> str:
    """
    Creates Telegram URL for downloading of file.

    - contains secret information (bot token)!

    :param file_path: `file_path` property of `File` object.
    """
    token = environ["TELEGRAM_API_BOT_TOKEN"]

    return create_url(
        "https://api.telegram.org/file",
        f"bot{token}",
        file_path
    )


def make_request(
    method_name: str,
    data: dict,
    files: dict = None
) -> dict:
    """
    Makes HTTP request to Telegram Bot API.

    - see `api/request.py` documentation for more.

    :param method_name: Name of API method in URL.
    :param data: JSON data to send. It will be sent as
    `application/json` payload.
    :param files: Files data to send. If specified, then
    `data` will be sent as query string. Files will be sent
    as `multipart/form-data` payload. See `files` for more -
    https://requests.readthedocs.io/en/latest/api/#requests.request

    :raises TelegramBotApiException:
    See `telegram/exceptions.py` documentation for more.
    """
    url = create_bot_url(method_name)
    timeout = current_app.config["TELEGRAM_API_TIMEOUT"]
    payload = {
        "json": data
    }

    if files:
        payload = {
            "files": files,
            "params": data
        }

    result = request(
        content_type="json",
        method="POST",
        url=url,
        timeout=timeout,
        allow_redirects=False,
        verify=True,
        **payload
    )
    ok = result["content"]["ok"]

    # 4xx or 5xx
    if not ok:
        raise RequestFailed(
            create_error_text(
                result["content"]
            )
        )

    # https://core.telegram.org/bots/api/#making-requests
    result["content"] = result["content"]["result"]

    return result


def create_error_text(error_response: dict) -> str:
    """
    Creates error text for Telegram Bot error response.
    See https://core.telegram.org/bots/api/#making-requests
    """
    description = error_response.get("description", "?")
    error_code = error_response.get("error_code", "?")

    return f"{error_code} ({description})"
