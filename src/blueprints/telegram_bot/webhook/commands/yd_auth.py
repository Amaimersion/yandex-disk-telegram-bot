import secrets

from flask import (
    g,
    current_app,
    url_for
)
import jwt

from src.database import (
    db,
    YandexDiskToken
)
from src.api import telegram, yandex
from src.blueprints.telegram_bot.utils import (
    get_current_datetime
)
from .common.decorators import (
    register_guest,
    get_db_data
)
from .common.responses import (
    request_private_chat,
    cancel_command
)
from . import CommandsNames


@register_guest
@get_db_data
def handle():
    """
    Handles `/yandex_disk_authorization` command.

    Authorization of bot in user Yandex.Disk.
    """
    user = g.db_user
    incoming_chat = g.db_chat
    private_chat = g.db_private_chat
    yd_token = user.yandex_disk_token

    if (private_chat is None):
        return request_private_chat(incoming_chat.telegram_id)

    if (yd_token is None):
        try:
            yd_token = create_empty_yd_token(user)
        except Exception as error:
            print(error)
            return cancel_command(private_chat.telegram_id)

    refresh_needed = False

    if (yd_token.have_access_token()):
        try:
            yd_token.get_access_token()

            telegram.send_message(
                chat_id=private_chat.telegram_id,
                text=(
                    "You already grant me access to your Yandex.Disk."
                    "\n"
                    "You can revoke my access with "
                    f"{CommandsNames.YD_REVOKE.value}"
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
            current_datetime = get_current_datetime()
            date = current_datetime["date"]
            time = current_datetime["time"]
            timezone = current_datetime["timezone"]

            telegram.send_message(
                chat_id=private_chat.telegram_id,
                parse_mode="HTML",
                text=(
                    "<b>Access to Yandex.Disk Refreshed</b>"
                    "\n\n"
                    "Your granted access was refreshed automatically by me "
                    f"on {date} at {time} {timezone}."
                    "\n\n"
                    "If it wasn't you, you can detach this access with "
                    f"{CommandsNames.YD_REVOKE.value}"
                )
            )

            return

    yd_token.clear_all_tokens()
    yd_token.set_insert_token(
        secrets.token_hex(
            current_app.config[
                "YANDEX_DISK_API_INSERT_TOKEN_BYTES"
            ]
        )
    )
    yd_token.insert_token_expires_in = (
        current_app.config[
            "YANDEX_DISK_API_INSERT_TOKEN_LIFETIME"
        ]
    )
    db.session.commit()

    insert_token = None

    try:
        insert_token = yd_token.get_insert_token()
    except Exception as error:
        print(error)
        return cancel_command(private_chat.telegram_id)

    if (insert_token is None):
        print("Error: Insert Token is NULL")
        return cancel_command(private_chat.telegram_id)

    state = jwt.encode(
        {
            "user_id": user.id,
            "insert_token": insert_token
        },
        current_app.secret_key.encode(),
        algorithm="HS256"
    ).decode()
    yandex_oauth_url = yandex.create_user_oauth_url(state)
    insert_token_lifetime = int(
        yd_token.insert_token_expires_in / 60
    )

    telegram.send_message(
        chat_id=private_chat.telegram_id,
        parse_mode="HTML",
        disable_web_page_preview=True,
        text=(
            'Open special link by pressing on "Grant access" '
            "button and grant me access to your Yandex.Disk."
            "\n\n"
            "<b>IMPORTANT: don't give this link to anyone, "
            "because it contains your secret information.</b>"
            "\n\n"
            f"<i>This link will expire in {insert_token_lifetime} minutes.</i>"
            "\n"
            "<i>This link leads to Yandex page and redirects to bot page.</i>"
            "\n\n"
            "<b>It is safe to give the access?</b>"
            "\n"
            "Yes! I'm getting access only to your Yandex.Disk, "
            "not to your account. You can revoke my access at any time with "
            f"{CommandsNames.YD_REVOKE.value} or in your "
            '<a href="https://passport.yandex.ru/profile">Yandex Profile</a>. '
            "By the way, i'm "
            f'<a href="{current_app.config["PROJECT_URL_FOR_CODE"]}">open-source</a> ' # noqa
            "and you can make sure that your data will be safe. "
            "You can even create your own bot with my functionality if using "
            "me makes you feel uncomfortable (:"
            "\n\n"
            "By using me, you accept "
            f'<a href="{url_for("legal.privacy_policy")}">Privacy Policy</a> and ' # noqa
            f'<a href="{url_for("legal.terms_and_conditions")}">Terms And Conditions</a>. ' # noqa
        ),
        reply_markup={"inline_keyboard": [
            [
                {
                    "text": "Grant access",
                    "url": yandex_oauth_url
                }
            ]
        ]}
    )


def create_empty_yd_token(user) -> YandexDiskToken:
    """
    Creates empty Yandex.Disk token and binds
    this to provided user.
    """
    new_yd_token = YandexDiskToken(user=user)

    db.session.add(new_yd_token)
    db.session.commit()

    return new_yd_token


def refresh_access_token(yd_token: YandexDiskToken) -> bool:
    """
    Tries to refresh user access token by using refresh token.

    :returns: `True` in case of success else `False`.
    """
    refresh_token = yd_token.get_refresh_token()

    if (refresh_token is None):
        return False

    result = None

    try:
        result = yandex.get_access_token(
            grant_type="refresh_token",
            refresh_token=refresh_token
        )
    except Exception as error:
        print(error)
        return False

    yandex_response = result["content"]

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
