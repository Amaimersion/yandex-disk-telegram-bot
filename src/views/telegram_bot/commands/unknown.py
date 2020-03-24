from flask import g

from ....api import telegram


def handle():
    """
    Handles unknown command.
    """
    telegram.send_message(
        chat_id=g.message["chat"]["id"],
        text="Unrecognized command. See command list or type /help"
    )
