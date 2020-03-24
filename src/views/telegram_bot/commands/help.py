from flask import g

from ....api import telegram


def handle():
    """
    Handles `/help` command.
    """
    telegram.send_message(
        chat_id=g.message["chat"]["id"],
        parse_mode="Markdown",
        text=(
            "I can help you to interact with Yandex.Disk."
            "\n\n"
            "Send me some data (images, files, etc.) and "
            "i think i will handle this. "
            "Moreover, you can control me by sending these commands:"
            "\n\n"
            "*Settings*"
            "\n"
            "/settings — full list of settings"
            "\n\n"
            "*Information*"
            "\n"
            "/about — read about me"
        )
    )
