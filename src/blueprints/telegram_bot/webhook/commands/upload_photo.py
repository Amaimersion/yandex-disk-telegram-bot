from flask import g

from .....api import telegram


def handle():
    """
    Handles `/upload_photo` command.
    """
    user = g.db_user
    chat = g.db_incoming_chat

    telegram.send_message(
        chat_id=chat.telegram_id,
        text="Success"
    )
