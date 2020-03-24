from flask import g

from ....api import telegram


def handle():
    """
    Handles `/about` command.
    """
    telegram.send_message(
        chat_id=g.message["chat"]["id"],
        text=(
            "I'm free and open-source bot that allows "
            "you to interact with Yandex.Disk through Telegram."
            "\n\n"
            "Written by Sergey Kuznetsov"
            "\n"
            "https://github.com/Amaimersion/yandex-disk-telegram-bot"
        )
    )
