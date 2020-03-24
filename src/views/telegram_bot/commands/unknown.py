from flask import g

from ....api import telegram


def handle():
    """
    Handles unknown command.
    """
    telegram.send_message(
        chat_id=g.message["chat"]["id"],
        text="Success from unknown command"
    )
