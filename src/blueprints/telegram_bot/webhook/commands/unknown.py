from flask import g

from src.api import telegram


def handle():
    """
    Handles unknown command.
    """
    telegram.send_message(
        chat_id=g.incoming_chat["id"],
        text=(
            "I can't understand this command. "
            "See command list or type /help"
        )
    )
