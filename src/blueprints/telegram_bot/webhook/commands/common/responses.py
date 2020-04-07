from ......api import telegram


def abort_command(chat_telegram_id: int) -> None:
    """
    Aborts command execution due to invalid message data.

    Don't confuse with `cancel_command()`.
    """
    telegram.send_message(
        chat_id=chat_telegram_id,
        text="I can't handle this because of your invalid data"
    )


def cancel_command(chat_telegram_id: int) -> None:
    """
    Cancels command execution due to internal server error.

    Don't confuse with `abort_command()`.
    """
    telegram.send_message(
        chat_id=chat_telegram_id,
        text=(
            "I can't process you because of my internal error. "
            "Try later please."
        )
    )


def request_private_chat(chat_telegram_id: int) -> None:
    """
    Aborts command execution due to lack of private chat with user.
    """
    telegram.send_message(
        chat_id=chat_telegram_id,
        text=(
            "I need to send you your sensitive information, "
            "but i don't know any private chat with you. "
            "Please contact me first through private chat (direct message). "
            "After that repeat your request."
        )
    )
