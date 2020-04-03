from datetime import datetime, timezone

from flask import g

from .....db import db
from .....api import telegram
from ..decorators import get_db_data


@get_db_data
def handle():
    """
    Handles `/yandex_disk_revoke` command.

    Revokes bot access to user Yandex.Disk
    """
    user = g.db_user
    private_chat = g.db_private_chat

    if (
        (user is None) or
        (user.yandex_disk_token is None) or
        (not user.yandex_disk_token.have_access_token())
    ):
        if (private_chat):
            telegram.send_message(
                chat_id=private_chat.telegram_id,
                text=(
                    "You don't gave me access to your Yandex.Disk."
                    "\n"
                    "You can do that with /yandex_disk_authorization"
                )
            )

        return

    user.yandex_disk_token.clear_all_tokens()
    db.session.commit()

    if (private_chat):
        current_datetime = datetime.now(timezone.utc)
        current_date = current_datetime.strftime("%d.%m.%Y")
        current_time = current_datetime.strftime("%H:%M:%S")
        current_timezone = current_datetime.strftime("%Z")

        telegram.send_message(
            chat_id=private_chat.telegram_id,
            parse_mode="HTML",
            disable_web_page_preview=True,
            text=(
                "<b>Access to Yandex.Disk Revoked</b>"
                "\n\n"
                "You successfully revoked my access to your Yandex.Disk "
                f"on {current_date} at {current_time} {current_timezone}."
                "\n\n"
                "Don't forget to do that at https://passport.yandex.ru/profile"
            )
        )
