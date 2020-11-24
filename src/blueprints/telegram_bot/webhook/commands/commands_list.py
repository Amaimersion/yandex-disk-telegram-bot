from collections import deque

from flask import g

from src.api import telegram
from ._common.commands_content import commands_html_content


def handle(*args, **kwargs):
    """
    Handles `/commands` command.
    """
    chat_id = kwargs.get(
        "chat_id",
        g.telegram_chat.id
    )
    text = create_commands_list_html_text()

    telegram.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML"
    )


def create_commands_list_html_text() -> str:
    text = deque()

    for group in commands_html_content:
        text.append(
            f"<b>{group['name']}</b>"
        )

        for command in group["commands"]:
            text.append(command["name"])

        text.append("")

    return "\n".join(text)
