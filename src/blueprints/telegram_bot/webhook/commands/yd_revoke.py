from datetime import datetime, timezone

from flask import g

from .....db import (
    db,
    UserQuery,
    ChatQuery
)
from .....api import telegram


def handle():
    """
    Handles `/yandex_disk_revoke` command.

    Revokes bot access to user Yandex.Disk
    """
    incoming_user_id = g.user["id"]
    user = UserQuery.get_user_by_telegram_id(incoming_user_id)
    yd_token = None
    private_chat = None

    if (user is not None):
        yd_token = user.yandex_disk_token
        private_chat = ChatQuery.get_private_chat(user.id)

    if (yd_token is None):
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

    yd_token.clear_all_tokens()
    db.session.commit()

    if (private_chat):
        current_datetime = datetime.now(timezone.utc)
        current_date = current_datetime.strftime("%d.%m.%Y")
        current_time = current_datetime.strftime("%H:%M:%S")
        current_timezone = current_datetime.strftime("%Z")

        telegram.send_message(
            chat_id=private_chat.telegram_id,
            parse_mode="HTML",
            text=(
                "<b>Access to Yandex.Disk Revoked</b>"
                "\n\n"
                "You successfully revoked my access to your Yandex.Disk "
                f"on {current_date} at {current_time} {current_timezone}."
                "\n\n"
                "Don't forget to do that at https://passport.yandex.ru/profile"
            )
        )
