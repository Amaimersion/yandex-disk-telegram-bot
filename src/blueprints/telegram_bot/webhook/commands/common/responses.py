from src.api import telegram


def abort_command(
    chat_telegram_id: int,
    message_telegram_id: int = None
) -> None:
    """
    Aborts command execution due to invalid message data.

    - don't confuse with `cancel_command()`.
    - if `message_telegram_id` specified, then
    that message will be updated.
    """
    text = (
        "I can't handle this because "
        "you didn't send any suitable data "
        "for that command."
    )

    if (message_telegram_id is None):
        telegram.send_message(
            chat_id=chat_telegram_id,
            text=text
        )
    else:
        telegram.edit_message_text(
            chat_id=chat_telegram_id,
            message_id=message_telegram_id,
            text=text
        )


def cancel_command(
    chat_telegram_id: int,
    message_telegram_id: int = None
) -> None:
    """
    Cancels command execution due to internal server error.

    - don't confuse with `abort_command()`.
    - if `message_telegram_id` specified, then
    that message will be updated.
    """
    text = (
        "At the moment i can't process this "
        "because of my internal error. "
        "Try later please."
    )

    if (message_telegram_id is None):
        telegram.send_message(
            chat_id=chat_telegram_id,
            text=text
        )
    else:
        telegram.edit_message_text(
            chat_id=chat_telegram_id,
            message_id=message_telegram_id,
            text=text
        )


def request_private_chat(chat_telegram_id: int) -> None:
    """
    Aborts command execution due to lack of private chat with user.
    """
    telegram.send_message(
        chat_id=chat_telegram_id,
        text=(
            "I need to send you your secret information, "
            "but i don't know any private chat with you. "
            "First, contact me through private chat (direct message). "
            "After that repeat your request."
        )
    )
