from flask import g

from src.database import (
    UserQuery,
    ChatQuery
)
from src.blueprints.telegram_bot._common import telegram_interface
from .dispatcher import direct_dispatch


def create_app_context(update: telegram_interface.Update):
    """
    Some app methods (decorators, for example) depends
    on specific application context (`g.telegram_user`, for example).
    This function will create needed application context.

    NOTE:
    you shouldn't use application context directly.
    Use it only when there is really no way to access needed data.

    NOTE:
    some data (for example, DB) may be not always available.
    Check for it before actual usage.

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

    if g.telegram_chat:
        g.db_chat = ChatQuery.get_chat_by_telegram_id(
            g.telegram_chat.id
        )

    # if it is new user (not yet registered in DB), then
    # DB data will be `None` for that user
    if g.db_user:
        g.db_private_chat = ChatQuery.get_private_chat(
            g.db_user.id
        )
