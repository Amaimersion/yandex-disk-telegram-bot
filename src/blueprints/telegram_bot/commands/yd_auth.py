import secrets

from flask import g, current_app

from ....db import (
    db,
    User,
    Chat,
    YandexDiskToken,
    UserQuery
)
from ....db.models import ChatType


def handle():
    """
    Handles `/yandex_disk_auth` command.

    Authorization of bot in user Yandex.Disk
    """
    incoming_telegram_id = g.user["id"]
    user = UserQuery.get_user_by_telegram_id(incoming_telegram_id)

    if (user is None):
        try:
            user = register_user()
        except Exception as e:
            print(e)
            return

    yd_token = user.yandex_disk_token

    if (yd_token is None):
        try:
            yd_token = create_empty_yd_token(user)
        except Exception as e:
            print(e)
            return

    if (yd_token.have_access_token()):
        try:
            yd_token.get_access_token()

            # `access_token` is valid
            return
        except Exception:
            # `access_token` is expired (most probably) or
            # data in DB is invalid
            pass

        if (yd_token.have_refresh_token()):
            # TODO: try to refresh
            pass

    yd_token.clear_all_token_data()
    yd_token.set_insert_token(
        secrets.token_hex(
            current_app.config["YD_API_INSERT_TOKEN_BYTES"]
        )
    )
    yd_token.insert_token_expires_in = (
        current_app.config["YD_API_INSERT_TOKEN_LIFETIME"]
    )
    db.session.commit()


def register_user() -> User:
    incoming_user = g.user
    incoming_chat = g.chat

    new_user = User(
        telegram_id=incoming_user["id"],
        is_bot=incoming_user.get("is_bot", False)
    )
    Chat(
        telegram_id=incoming_chat["id"],
        type=ChatType.get(incoming_chat["type"]),
        user=new_user
    )

    db.session.add(new_user)
    db.session.commit()

    return new_user


def create_empty_yd_token(user: User) -> YandexDiskToken:
    new_yd_token = YandexDiskToken(user=user)

    db.session.add(new_yd_token)
    db.session.commit()

    return new_yd_token
