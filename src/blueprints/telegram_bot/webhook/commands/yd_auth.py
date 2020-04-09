import os
import secrets
import base64
from datetime import datetime, timezone

from flask import g, current_app
import jwt

from .....db import (
    db,
    YandexDiskToken
)
from .....api import telegram, yandex
from .common.decorators import (
    register_guest,
    get_db_data
)
from .common.responses import (
    request_private_chat,
    cancel_command
)
from .common.names import CommandNames


@register_guest
@get_db_data
def handle():
    """
    Handles `/yandex_disk_authorization` command.

    Authorization of bot in user Yandex.Disk
    """
    user = g.db_user
    incoming_chat = g.db_incoming_chat
    private_chat = g.db_private_chat
    yd_token = user.yandex_disk_token

    if (yd_token is None):
        try:
            yd_token = create_empty_yd_token(user)
        except Exception as e:
            print(e)
            return cancel_command(incoming_chat.telegram_id)

    refresh_needed = False

    if (yd_token.have_access_token()):
        try:
            yd_token.get_access_token()

            if (private_chat):
                telegram.send_message(
                    chat_id=private_chat.telegram_id,
                    text=(
                        "You already gave me access to your Yandex.Disk."
                        "\n"
                        "If you want to revoke access, then do that with "
                        f"{CommandNames.YD_REVOKE}"
                    )
                )

            # `access_token` is valid
            return
        except Exception:
            # `access_token` is expired (most probably) or
            # data in DB is invalid
            refresh_needed = True

    if (refresh_needed):
        success = refresh_access_token(yd_token)

        if (success):
            if (private_chat):
                current_datetime = datetime.now(timezone.utc)
                current_date = current_datetime.strftime("%d.%m.%Y")
                current_time = current_datetime.strftime("%H:%M:%S")
                current_timezone = current_datetime.strftime("%Z")

                telegram.send_message(
                    chat_id=private_chat.telegram_id,
                    parse_mode="HTML",
                    text=(
                        "<b>Access to Yandex.Disk Updated</b>"
                        "\n\n"
                        "Your granted access was updated automatically "
                        f"on {current_date} at {current_time} "
                        f"{current_timezone}."
                        "\n\n"
                        "If it wasn't you, you can detach this access with "
                        f"{CommandNames.YD_REVOKE}"
                    )
                )

            return

    yd_token.clear_all_tokens()
    yd_token.set_insert_token(
        secrets.token_hex(
            current_app.config["YANDEX_DISK_API_INSERT_TOKEN_BYTES"]
        )
    )
    yd_token.insert_token_expires_in = (
        current_app.config["YANDEX_DISK_API_INSERT_TOKEN_LIFETIME"]
    )
    db.session.commit()

    insert_token = None

    try:
        insert_token = yd_token.get_insert_token()
    except Exception as e:
        print(e)
        return cancel_command(incoming_chat.telegram_id)

    if (insert_token is None):
        print("Error: Insert Token is NULL")
        return cancel_command(incoming_chat.telegram_id)

    state = jwt.encode(
        {
            "user_id": user.id,
            "insert_token": insert_token
        },
        current_app.secret_key.encode(),
        algorithm="HS256"
    ).decode()
    yandex_oauth_url = create_yandex_oauth_url(state)
    insert_token_lifetime = int(
        yd_token.insert_token_expires_in / 60
    )

    if (private_chat is None):
        return request_private_chat(incoming_chat.telegram_id)

    telegram.send_message(
        chat_id=private_chat.telegram_id,
        parse_mode="HTML",
        disable_web_page_preview=True,
        text=(
            "Follow this link and allow me access to your "
            f"Yandex.Disk — {yandex_oauth_url}"
            "\n\n"
            "<b>IMPORTANT: don't give this link to anyone, "
            "because it contains your sensitive information.</b>"
            "\n\n"
            f"<i>This link will expire in {insert_token_lifetime} minutes.</i>"
            "\n"
            "<i>This link leads to Yandex page and redirects to bot page.</i>"
        )
    )


def create_empty_yd_token(user) -> YandexDiskToken:
    new_yd_token = YandexDiskToken(user=user)

    db.session.add(new_yd_token)
    db.session.commit()

    return new_yd_token


def create_yandex_oauth_url(state: str) -> str:
    client_id = os.getenv("YANDEX_OAUTH_API_APP_ID", "")
    state = base64.urlsafe_b64encode(
        state.encode()
    ).decode()

    return (
        "https://oauth.yandex.ru/authorize?"
        "response_type=code"
        f"&client_id={client_id}"
        f"&state={state}"
    )


def refresh_access_token(yd_token) -> bool:
    refresh_token = yd_token.get_refresh_token()

    if (refresh_token is None):
        return False

    yandex_response = None

    try:
        yandex_response = yandex.get_access_token(
            grant_type="refresh_token",
            refresh_token=refresh_token
        )
    except Exception as e:
        print(e)
        return False

    if ("error" in yandex_response):
        return False

    yd_token.clear_insert_token()
    yd_token.set_access_token(
        yandex_response["access_token"]
    )
    yd_token.access_token_type = (
        yandex_response["token_type"]
    )
    yd_token.access_token_expires_in = (
        yandex_response["expires_in"]
    )
    yd_token.set_refresh_token(
        yandex_response["refresh_token"]
    )
    db.session.commit()

    return True
