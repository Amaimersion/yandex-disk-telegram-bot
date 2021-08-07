from flask import g

from src.http import telegram
from src.i18n import gettext
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
        text=gettext(
            "I don't know this command. "
            "See commands list or type %(help_command)s",
            help_command=CommandName.HELP.value
        )
    )
