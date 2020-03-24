from flask import g

from ....api import telegram


def handle():
    telegram.send_message(
        chat_id=g.message["chat"]["id"],
        text="Success from /help"
    )
