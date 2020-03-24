import requests

from .request import make_request

from .exceptions import TelegramApiException


def send_message(**kwargs) -> None:
    """
    https://core.telegram.org/bots/api/#sendmessage
    """
    try:
        make_request("sendMessage", kwargs)
    except requests.RequestException as error:
        print(error)
    except TelegramApiException as error:
        print(error)
