from flask import g

from .....api import telegram
from ..views import get_text


def handle():
    """
    Handles `/create_folder` command.
    """
    message_text = get_text(g.incoming_message)
    folder_name = message_text.replace("/create_folder", "").strip()

    telegram.send_message(
        chat_id=g.incoming_chat["id"],
        text=folder_name
    )
