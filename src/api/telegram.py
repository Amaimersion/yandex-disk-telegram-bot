import os

import requests


def _create_url(method_name: str) -> str:
    """
    Creates Telegram API URL for calling.
    """
    base = "https://api.telegram.org"
    bot = "bot{token}".format(token=os.getenv("TELEGRAM_BOT_API_TOKEN", ""))
    url = f"{base}/{bot}/{method_name}"

    return url


def _make_request(method_name: str, data: dict) -> None:
    """
    Makes API request to Telegram.
    """
    url = _create_url(method_name)

    # we will not handle any errors at the moment
    requests.post(url, data)


def send_message(data: dict) -> None:
    """
    https://core.telegram.org/bots/api/#sendmessage
    """
    _make_request("sendMessage", data)
