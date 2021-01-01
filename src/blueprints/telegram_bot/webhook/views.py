from flask import (
    request,
    g,
    make_response
)

from src.blueprints.telegram_bot import telegram_bot_blueprint as bp
from src.blueprints.telegram_bot._common import telegram_interface
from .dispatcher import intellectual_dispatch, direct_dispatch


@bp.route("/webhook", methods=["POST"])
def webhook():
    """
    Handles Webhook POST request from Telegram server.

    - for Webhook we always should return 200 to indicate
    that we successfully got an update, otherwise Telegram
    will flood the server. So, not use `abort()` or anything.
    """
    raw_data = request.get_json(
        force=True,
        silent=True,
        cache=False
    )

    if raw_data is None:
        return make_error_response()

    telegram_update = telegram_interface.Update(raw_data)

    if not telegram_update.is_valid():
        return make_error_response()

    message = telegram_update.get_message()

    if not message.is_valid():
        return make_error_response()

    g.telegram_message = message
    g.telegram_user = message.get_user()
    g.telegram_chat = message.get_chat()
    g.direct_dispatch = direct_dispatch

    # We call this handler and do not handle any errors.
    # We assume that all errors already was handeld by
    # handlers, loggers, etc.
    # WARNING: in case of any exceptions there will be
    # 500 from a server. Telegram will send user message
    # again and again until it get 200 from a server.
    # So, it is important to always return 200 or return
    # 500 and expect same message again
    intellectual_dispatch(message)()

    return make_success_response()


def make_error_response():
    """
    Creates error response for Telegram Webhook.
    """
    return make_response((
        {
            "ok": False,
            "error_code": 400
        },
        200
    ))


def make_success_response():
    """
    Creates success response for Telegram Webhook.
    """
    return make_response((
        {
            "ok": True
        },
        200
    ))
