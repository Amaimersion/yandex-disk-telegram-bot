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


def get_file(**kwargs) -> dict:
    """
    https://core.telegram.org/bots/api#getfile
    """
    return make_request("getFile", kwargs)


def send_chat_action(**kwargs) -> dict:
    """
    https://core.telegram.org/bots/api/#sendchataction
    """
    return make_request("sendChatAction", kwargs)
