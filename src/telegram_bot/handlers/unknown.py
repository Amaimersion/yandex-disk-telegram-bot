from flask import g

from ...api.telegram import send_message


def handle():
    send_message({
        "chat_id": g.message["chat"]["id"],
        "text": "Success from unknown command handler"
    })
