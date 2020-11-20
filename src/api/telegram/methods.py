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


def send_photo(**kwargs):
    """
    https://core.telegram.org/bots/api#sendphoto

    - see `api/request.py` documentation for more.
    - if you want to send bytes, then specify `photo` as
    tuple from `files` in
    https://requests.readthedocs.io/en/latest/api/#requests.request
    """
    files = None
    key = "photo"
    value = kwargs.get(key)

    if not isinstance(value, str):
        files = {
            key: kwargs.pop(key)
        }

    return make_request("sendPhoto", data=kwargs, files=files)
