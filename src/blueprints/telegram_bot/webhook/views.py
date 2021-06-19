from flask import (
    request,
    g,
    make_response
)

from src.database import (
    User,
    UserQuery,
    Chat,
    ChatQuery,
    UserSettings
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

    update = telegram_interface.Update(raw_data)

    create_app_context(update)

    handler = intellectual_dispatch(update)

    if not handler:
        return make_error_response()

    # We call this handler and do not handle any errors.
    # We assume that all errors already was handeld by
    # handlers, loggers, etc.
    # WARNING: in case of any exceptions there will be
    # 500 from a server. Telegram will send user message
    # again and again until it get 200 from a server.
    # So, it is important to always return 200 or return
    # 500 and expect same message again
    handler()

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


def create_app_context(update: telegram_interface.Update):
    """
    Some app methods (decorators, for example) depends
    on specific application context (`g.telegram_user`, for example).
    This function will create needed application context.

    NOTE:
    you shouldn't use application context directly.
    Use it only when there is really no way to access needed data.

    NOTE:
    some data may be not always available. Check it before usage.

    - https://flask.palletsprojects.com/en/1.1.x/appcontext/
    """
    message = update.get_message()
    callback_query = update.get_callback_query()

    if (not message and callback_query):
        message = callback_query.get_message()

    # all possible properties in global context with defaults
    g.telegram_message = None
    g.telegram_callback_query = None
    g.telegram_user = None
    g.telegram_chat = None
    g.db_user = None
    g.db_chat = None
    g.db_private_chat = None
    g.direct_dispatch = direct_dispatch

    if message:
        g.telegram_message = message
        g.telegram_user = message.get_user()
        g.telegram_chat = message.get_chat()

    if callback_query:
        g.telegram_callback_query = callback_query

        # if `callback_query` exists and `message` not,
        # then `update.callback_query.from` will have
        # actual result than `update.callback_query.message.from`.
        g.telegram_user = callback_query.get_user()

    if g.telegram_user:
        g.db_user = UserQuery.get_user_by_telegram_id(
            g.telegram_user.id
        )
        g.db_private_chat = ChatQuery.get_private_chat(
            g.db_user.id
        )

    if g.telegram_chat:
        g.db_chat = ChatQuery.get_chat_by_telegram_id(
            g.telegram_chat.id
        )
