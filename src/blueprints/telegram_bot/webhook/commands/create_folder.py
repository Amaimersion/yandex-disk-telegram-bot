from flask import g

from .....api import telegram


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


def get_text(message: dict) -> str:
    """
    Extracts text from a message.
    """
    return (
        message.get("text") or
        message.get("caption") or
        ""
    )
