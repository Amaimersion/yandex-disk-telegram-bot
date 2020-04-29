from flask import g

from src.database import db
from src.api import telegram
from src.blueprints.utils import get_current_datetime
from .common.decorators import get_db_data
from .common.responses import request_private_chat
from . import CommandsNames


@get_db_data
def handle():
    """
    Handles `/yandex_disk_revoke` command.

    Revokes bot access to user Yandex.Disk.
    """
    user = g.db_user
    incoming_chat = g.db_chat
    private_chat = g.db_private_chat

    if (private_chat is None):
        return request_private_chat(incoming_chat.telegram_id)

    if (
        (user is None) or
        (user.yandex_disk_token is None) or
        (not user.yandex_disk_token.have_access_token())
    ):
        telegram.send_message(
            chat_id=private_chat.telegram_id,
            text=(
                "You don't granted me access to your Yandex.Disk."
                "\n"
                f"You can do that with {CommandsNames.YD_AUTH.value}"
            )
        )

        return

    user.yandex_disk_token.clear_all_tokens()
    db.session.commit()

    current_datetime = get_current_datetime()
    date = current_datetime["date"]
    time = current_datetime["time"]
    timezone = current_datetime["timezone"]

    telegram.send_message(
        chat_id=private_chat.telegram_id,
        parse_mode="HTML",
        disable_web_page_preview=True,
        text=(
            "<b>Access to Yandex.Disk Revoked</b>"
            "\n\n"
            "You successfully revoked my access to your Yandex.Disk "
            f"on {date} at {time} {timezone}."
            "\n\n"
            "Don't forget to do that in your "
            '<a href="https://passport.yandex.ru/profile">Yandex Profile</a>.'
        )
    )
