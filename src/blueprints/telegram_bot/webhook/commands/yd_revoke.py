from flask import g

from src.extensions import db
from src.http import telegram
from src.i18n import gettext
from src.blueprints._common.utils import get_current_datetime
from src.blueprints.telegram_bot._common.yandex_oauth import YandexOAuthClient
from ._common.decorators import (
    register_guest
)
from ._common.responses import (
    request_private_chat,
    cancel_command
)
from src.blueprints.telegram_bot._common.command_names import CommandName


class YandexOAuthRemoveClient(YandexOAuthClient):
    def clear_access_token(self, db_user) -> None:
        super().clear_access_token(db_user)
        db.session.commit()


@register_guest
def handle(*args, **kwargs):
    """
    Handles `/revoke_access` command.

    Revokes bot access to user Yandex.Disk.
    """
    private_chat = g.db_private_chat

    if private_chat is None:
        incoming_chat_id = kwargs.get(
            "chat_id",
            g.telegram_chat.id
        )

        return request_private_chat(incoming_chat_id)

    user = g.db_user
    chat_id = private_chat.telegram_id
    client = YandexOAuthRemoveClient()

    if (
        (user is None) or
        not client.have_valid_access_token(user)
    ):
        return message_dont_have_access_token(chat_id)

    try:
        client.clear_access_token(user)
    except Exception as error:
        cancel_command(chat_id)
        raise error

    message_access_token_removed(chat_id)


# region Messages


def message_dont_have_access_token(chat_id: int) -> None:
    telegram.send_message(
        chat_id=chat_id,
        text=gettext(
            "You don't granted me access to your Yandex.Disk."
            "\n"
            "You can do that with %(yd_auth_command)s",
            yd_auth_command=CommandName.YD_AUTH.value
        )
    )


def message_access_token_removed(chat_id: int) -> None:
    now = get_current_datetime()
    date = now["date"]
    time = now["time"]
    timezone = now["timezone"]

    telegram.send_message(
        chat_id=chat_id,
        parse_mode="HTML",
        disable_web_page_preview=True,
        text=gettext(
            "<b>Access to Yandex.Disk Revoked</b>"
            "\n\n"
            "You successfully revoked my access to your Yandex.Disk "
            "on %(date)s at %(time)s %(timezone)s."
            "\n\n"
            "Don't forget to do that in your "
            '<a href="https://passport.yandex.ru/profile">Yandex Profile</a>.'
            "\n"
            "To grant access again use %(yd_auth_command)s",
            date=date,
            time=time,
            timezone=timezone,
            yd_auth_command=CommandName.YD_AUTH.value
        )
    )


# endregion
