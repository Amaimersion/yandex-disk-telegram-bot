from .requests import make_request


def send_message(**kwargs):
    """
    https://core.telegram.org/bots/api/#sendmessage

    - see `api/request.py` documentation for more.
    """
    return make_request("sendMessage", kwargs)


def get_file(**kwargs):
    """
    https://core.telegram.org/bots/api#getfile

    - see `api/request.py` documentation for more.
    """
    return make_request("getFile", kwargs)


def send_chat_action(**kwargs):
    """
    https://core.telegram.org/bots/api/#sendchataction

    - see `api/request.py` documentation for more.
    """
    return make_request("sendChatAction", kwargs)


def edit_message_text(**kwargs):
    """
    https://core.telegram.org/bots/api/#editmessagetext

    - see `api/request.py` documentation for more.
    """
    return make_request("editMessageText", kwargs)
