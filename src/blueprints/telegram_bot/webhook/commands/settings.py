from flask import g

from src.api import telegram
from src.blueprints.telegram_bot._common.yandex_oauth import (
    YandexOAuthClient
)
from ._common.decorators import (
    register_guest,
    get_db_data
)
from ._common.responses import (
    request_private_chat
)


@register_guest
@get_db_data
def handle(*args, **kwargs):
    """
    Handles `/settings` command.
    """
    private_chat = g.db_private_chat

    if private_chat is None:
        incoming_chat_id = kwargs.get(
            "chat_id",
            g.db_chat.telegram_id
        )

        return request_private_chat(incoming_chat_id)

    user = g.db_user
    yo_client = YandexOAuthClient()
    yd_access = False

    if yo_client.have_valid_access_token(user):
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
