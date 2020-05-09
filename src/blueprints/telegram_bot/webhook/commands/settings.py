from flask import g

from src.api import telegram
from .common.decorators import (
    register_guest,
    get_db_data
)
from .common.responses import (
    request_private_chat
)


@register_guest
@get_db_data
def handle():
    """
    Handles `/settings` command.
    """
    user = g.db_user
    incoming_chat = g.db_chat
    private_chat = g.db_private_chat

    if (private_chat is None):
        return request_private_chat(incoming_chat.telegram_id)

    yd_access = False

    if (
        (user.yandex_disk_token) and
        (user.yandex_disk_token.have_access_token())
    ):
        yd_access = True

    text = (
        "<b>Preferred language:</b> "
        f"{user.language.name}"
        "\n"
        "<b>Yandex.Disk Access:</b> "
        f"{'Given' if yd_access else 'Revoked'}"
    )

    telegram.send_message(
        chat_id=private_chat.telegram_id,
        parse_mode="HTML",
        text=text
    )
