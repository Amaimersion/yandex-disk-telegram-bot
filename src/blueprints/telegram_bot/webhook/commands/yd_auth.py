from flask import g, current_app

from src.api import telegram
from src.configs.flask import YandexOAuthAPIMethod
from src.blueprints._common.utils import (
    absolute_url_for,
    get_current_datetime
)
from src.blueprints.telegram_bot._common import yandex_oauth
from src.blueprints.telegram_bot._common.stateful_chat import (
    stateful_chat_is_enabled,
    set_disposable_handler,
    set_user_chat_data,
    get_user_chat_data,
    delete_user_chat_data
)
from src.blueprints.telegram_bot.webhook.dispatcher_interface import (
    DispatcherEvent,
    RouteSource
)
from ._common.decorators import (
    register_guest
)
from ._common.responses import (
    request_private_chat,
    cancel_command
)
from src.blueprints.telegram_bot._common.command_names import CommandName


@register_guest
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
    route_source = kwargs.get("route_source")

    # console client is waiting for user code
    if (route_source == RouteSource.DISPOSABLE_HANDLER):
        return end_console_client(
            user,
            chat_id,
            kwargs["message"].get_plain_text()
        )

    oauth_method = current_app.config.get("YANDEX_OAUTH_API_METHOD")

    if (oauth_method == YandexOAuthAPIMethod.AUTO_CODE_CLIENT):
        run_auto_code_client(user, chat_id)
    elif (oauth_method == YandexOAuthAPIMethod.CONSOLE_CLIENT):
        start_console_client(user, chat_id)
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


def start_console_client(db_user, chat_id: int) -> None:
    if not stateful_chat_is_enabled():
        cancel_command(chat_id)
        raise Exception("Stateful chat is required to be enabled")

    client = yandex_oauth.YandexOAuthConsoleClient()
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
        message_grant_access_code(
            chat_id,
            result["url"],
            result["lifetime"]
        )
        # we will pass this state later
        set_user_chat_data(
            db_user.telegram_id,
            chat_id,
            "yandex_oauth_console_client_state",
            result["state"],
            result["lifetime"]
        )
        # on next plain text message we will handle provided code
        set_disposable_handler(
            db_user.telegram_id,
            chat_id,
            CommandName.YD_AUTH.value,
            [DispatcherEvent.PLAIN_TEXT.value],
            result["lifetime"]
        )
    else:
        cancel_command(chat_id)
        raise Exception("Unknown operation status")


def end_console_client(db_user, chat_id: int, code: str) -> None:
    state = get_user_chat_data(
        db_user.telegram_id,
        chat_id,
        "yandex_oauth_console_client_state"
    )
    delete_user_chat_data(
        db_user.telegram_id,
        chat_id,
        "yandex_oauth_console_client_state"
    )

    if not state:
        return telegram.send_message(
            chat_id=chat_id,
            text=(
                "You waited too long. "
                f"Send {CommandName.YD_AUTH} again."
            )
        )

    client = yandex_oauth.YandexOAuthConsoleClient()
    result = None
    message = None

    try:
        result = client.handle_code(state, code)
    except yandex_oauth.InvalidState:
        message = (
            "Your credentials is not valid. "
            f"Try send {CommandName.YD_AUTH} again."
        )
    except yandex_oauth.ExpiredInsertToken:
        message = (
            "You waited too long. "
            f"Send {CommandName.YD_AUTH} again."
        )
    except yandex_oauth.InvalidInsertToken:
        message = (
            "You have too many authorization sessions. "
            f"Send {CommandName.YD_AUTH} again and use only last link."
        )
    except Exception as error:
        cancel_command(chat_id)
        raise error

    if message:
        return telegram.send_message(
            chat_id=chat_id,
            text=message
        )

    if not result["ok"]:
        error = result["error"]
        title = error.get(
            "title",
            "Unknown error"
        )
        description = error.get(
            "description",
            "Can't tell you more"
        )

        return telegram.send_message(
            chat_id=chat_id,
            parse_mode="HTML",
            text=(
                "<b>Yandex.OAuth Error</b>"
                "\n\n"
                f"<b>Error</b>: {title}"
                "\n"
                f"<b>Description</b>: {description}"
                "\n\n"
                "I still don't have access. "
                f"Start new session using {CommandName.YD_AUTH.value}"
            )
        )

    message_access_token_granted(chat_id)


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


def message_access_token_granted(chat_id: int) -> None:
    now = get_current_datetime()
    date = now["date"]
    time = now["time"]
    timezone = now["timezone"]

    telegram.send_message(
        chat_id=chat_id,
        parse_mode="HTML",
        text=(
            "<b>Access to Yandex.Disk Granted</b>"
            "\n\n"
            "My access was attached to your Telegram account "
            f"on {date} at {time} {timezone}."
            "\n\n"
            "If it wasn't you, then detach this access with "
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


def message_grant_access_code(
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
            "<i>This link leads to Yandex page. After granting access, "
            "you will need to send me the issued code.</i>"
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
    # TODO:
    # React on press of inline keyboard button
    # (https://core.telegram.org/bots/api#callbackquery),
    # not send separate message immediately.
    # But it requires refactoring of dispatcher and others.
    # At the moment let it be implemented as it is,
    # because "Console Client" is mostly for developers, not users.
    telegram.send_message(
        chat_id=chat_id,
        text=(
            "Open this link, grant me an access "
            "and then send me a code"
        )
    )


# endregion
