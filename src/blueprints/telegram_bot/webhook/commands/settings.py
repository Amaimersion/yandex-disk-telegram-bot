from flask import g

from .....api import telegram
from ..decorators import register_guest, get_db_data


@register_guest
@get_db_data
def handle():
    """
    Handles `/settings` command.
    """
    user = g.db_user
    private_chat = g.private_chat

    if (private_chat is None):
        return

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
        f"{'Granted' if yd_access else 'Not Granted'}"
    )

    telegram.send_message(
        chat_id=private_chat.telegram_id,
        parse_mode="HTML",
        text=text
    )
