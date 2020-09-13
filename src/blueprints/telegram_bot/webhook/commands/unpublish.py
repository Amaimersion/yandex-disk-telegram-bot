from flask import g

from src.api import telegram
from .common.responses import (
    cancel_command,
    abort_command,
    AbortReason
)
from .common.decorators import (
    yd_access_token_required,
    get_db_data
)
from .common.yandex_api import (
    unpublish_item,
    YandexAPIUnpublishItemError,
    YandexAPIRequestError
)
from . import CommandsNames


@yd_access_token_required
@get_db_data
def handle():
    """
    Handles `/unpublish` command.
    """
    message = g.telegram_message
    user = g.db_user
    chat = g.db_chat
    message_text = message.get_text()
    path = message_text.replace(
        CommandsNames.UNPUBLISH.value,
        ""
    ).strip()

    if not (path):
        return abort_command(
            chat.telegram_id,
            AbortReason.NO_SUITABLE_DATA
        )

    access_token = user.yandex_disk_token.get_access_token()

    try:
        unpublish_item(
            access_token,
            path
        )
    except YandexAPIRequestError as error:
        print(error)
        return cancel_command(chat.telegram_id)
    except YandexAPIUnpublishItemError as error:
        error_text = (
            str(error) or
            "Unknown Yandex.Disk error"
        )

        telegram.send_message(
            chat_id=chat.telegram_id,
            text=error_text
        )

        return

    telegram.send_message(
        chat_id=chat.telegram_id,
        text="Unpublished"
    )
