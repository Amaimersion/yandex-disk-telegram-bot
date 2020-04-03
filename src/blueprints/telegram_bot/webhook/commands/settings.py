from flask import g

from .....api import telegram


def handle():
    """
    Handles `/settings` command.
    """
    telegram.send_message(
        chat_id=g.incoming_message["id"],
        parse_mode="HTML",
        text="/settings"
    )
