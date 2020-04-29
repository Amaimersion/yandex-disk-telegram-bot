from flask import g

from src.api import telegram
from . import CommandsNames


def handle():
    """
    Handles unknown command.
    """
    telegram.send_message(
        chat_id=g.telegram_chat.id,
        text=(
            "I don't know this command. "
            f"See commands list or type {CommandsNames.HELP.value}"
        )
    )
