from flask import g, current_app

from src.api import telegram
from src.configs.flask import YandexOAuthAPIMethod
from src.blueprints.utils import (
    absolute_url_for,
    get_current_datetime
)
from src.blueprints.telegram_bot._common import yandex_oauth
from .common.decorators import (
    register_guest,
    get_db_data
)
from .common.responses import (
    request_private_chat,
    cancel_command
)
from . import CommandName


@register_guest
@get_db_data
def handle(*args, **kwargs):
    """
    Handles `/grant_access` command.

    Allowing to bot to use user Yandex.Disk.
    """
    private_chat = g.db_private_chat

    # we allow to use this command only in
    # private chats for security reasons
    if private_chat is None:
        incoming_chat_id = kwargs.get(
            "chat_id",
            g.db_chat.telegram_id
        )

        return request_private_chat(incoming_chat_id)

    user = g.db_user
    chat_id = private_chat.telegram_id
    oauth_method = current_app.config.get("YANDEX_OAUTH_API_METHOD")

    if (oauth_method == YandexOAuthAPIMethod.AUTO_CODE_CLIENT):
        run_auto_code_client(user, chat_id)
    elif (oauth_method == YandexOAuthAPIMethod.CONSOLE_CLIENT):
        run_console_client(user, chat_id)
    else:
        cancel_command(chat_id)
        raise Exception("Unknown Yandex.OAuth method")


def run_auto_code_client(db_user, chat_id: int) -> None:
    client = yandex_oauth.YandexOAuthAutoCodeClient()
    result = None

    try:
        result = client.before_user_interaction(db_user)
    except Exception as error:
        cancel_command(chat_id)
        raise error

    status = result["status"]

    if (status == yandex_oauth.OperationStatus.HAVE_ACCESS_TOKEN):
        message_have_access_token(chat_id)
    elif (status == yandex_oauth.OperationStatus.ACCESS_TOKEN_REFRESHED):
        message_access_token_refreshed(chat_id)
    elif (status == yandex_oauth.OperationStatus.CONTINUE_TO_URL):
        # only in that case further user actions is needed
        message_grant_access_redirect(
            chat_id,
            result["url"],
            result["lifetime"]
        )
    else:
        cancel_command(chat_id)
        raise Exception("Unknown operation status")


def run_console_client(db_user, chat_id: int) -> None:
    pass


# region Messages


def message_have_access_token(chat_id: int) -> None:
    telegram.send_message(
        chat_id=chat_id,
        text=(
            "You already grant me access to your Yandex.Disk."
            "\n"
            "You can revoke my access with "
            f"{CommandName.YD_REVOKE.value}"
        )
    )


def message_access_token_refreshed(chat_id: int) -> None:
    now = get_current_datetime()
    date = now["date"]
    time = now["time"]
    timezone = now["timezone"]

    telegram.send_message(
        chat_id=chat_id,
        parse_mode="HTML",
        text=(
            "<b>Access to Yandex.Disk Refreshed</b>"
            "\n\n"
            "Your granted access was refreshed automatically by me "
            f"on {date} at {time} {timezone}."
            "\n\n"
            "If it wasn't you, you can detach this access with "
            f"{CommandName.YD_REVOKE.value}"
        )
    )


def message_grant_access_redirect(
    chat_id: int,
    url: str,
    lifetime_in_seconds: int
) -> None:
    open_link_button_text = "Grant access"
    revoke_command = CommandName.YD_REVOKE.value
    yandex_passport_url = "https://passport.yandex.ru/profile"
    source_code_url = current_app.config["PROJECT_URL_FOR_CODE"]
    privacy_policy_url = absolute_url_for("legal.privacy_policy")
    terms_url = absolute_url_for("legal.terms_and_conditions")
    lifetime_in_minutes = int(lifetime_in_seconds / 60)

    telegram.send_message(
        chat_id=chat_id,
        parse_mode="HTML",
        disable_web_page_preview=True,
        text=(
            f'Open special link by pressing on "{open_link_button_text}" '
            "button and grant me access to your Yandex.Disk."
            "\n\n"
            "<b>IMPORTANT: don't give this link to anyone, "
            "because it contains your secret information.</b>"
            "\n\n"
            f"<i>This link will expire in {lifetime_in_minutes} minutes.</i>"
            "\n"
            "<i>This link leads to Yandex page and redirects to bot page.</i>"
            "\n\n"
            "<b>It is safe to give the access?</b>"
            "\n"
            "Yes! I'm getting access only to your Yandex.Disk, "
            "not to your account. You can revoke my access at any time "
            f"with {revoke_command} or in your "
            f'<a href="{yandex_passport_url}">Yandex profile</a>. '
            "By the way, i'm "
            f'<a href="{source_code_url}">open-source</a> '
            "and you can make sure that your data will be safe. "
            "You can even create your own bot with my functionality "
            "if using me makes you feel uncomfortable (:"
            "\n\n"
            "By using me, you accept "
            f'<a href="{privacy_policy_url}">Privacy Policy</a> and '
            f'<a href="{terms_url}">Terms of service</a>. '
        ),
        reply_markup={
            "inline_keyboard": [
                [
                    {
                        "text": open_link_button_text,
                        "url": url
                    }
                ]
            ]
        }
    )


# endregion
