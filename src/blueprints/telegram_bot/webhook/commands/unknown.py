from flask import g

from src.api import telegram
from src.blueprints.telegram_bot._common.command_names import CommandName


def handle(*args, **kwargs):
    """
    Handles unknown command.
    """
    telegram.send_message(
        chat_id=kwargs.get(
            "chat_id",
            g.telegram_chat.id
        ),
        text=(
            "I don't know this command. "
            f"See commands list or type {CommandName.HELP.value}"
        )
    )
