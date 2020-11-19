from flask import g, current_app

from src.api import telegram
from src.blueprints.telegram_bot._common.yandex_disk import (
    create_folder,
    YandexAPICreateFolderError,
    YandexAPIRequestError
)
from src.blueprints.telegram_bot._common.command_names import (
    CommandName
)
from src.blueprints.telegram_bot._common.stateful_chat import (
    set_disposable_handler
)
from src.blueprints.telegram_bot.webhook.dispatcher_events import (
    DispatcherEvent,
    RouteSource
)
from ._common.responses import cancel_command
from ._common.decorators import (
    yd_access_token_required,
    get_db_data
)


@yd_access_token_required
@get_db_data
def handle(*args, **kwargs):
    message = kwargs.get(
        "message",
        g.telegram_message
    )
    user_id = kwargs.get(
        "user_id",
        g.telegram_user.id
    )
    chat_id = kwargs.get(
        "chat_id",
        g.telegram_chat.id
    )
    folder_name = get_folder_name(
        message,
        kwargs.get("route_source")
    )

    if not folder_name:
        set_disposable_handler(
            user_id,
            chat_id,
            CommandName.CREATE_FOLDER.value,
            [
                DispatcherEvent.PLAIN_TEXT.value,
                DispatcherEvent.BOT_COMMAND.value,
                DispatcherEvent.EMAIL.value,
                DispatcherEvent.HASHTAG.value,
                DispatcherEvent.URL.value
            ],
            current_app.config["RUNTIME_DISPOSABLE_HANDLER_EXPIRE"]
        )

        return message_wait_for_text(chat_id)

    user = g.db_user
    access_token = user.yandex_disk_token.get_access_token()
    last_status_code = None

    try:
        last_status_code = create_folder(
            user_access_token=access_token,
            folder_name=folder_name
        )
    except YandexAPIRequestError as error:
        cancel_command(chat_id)
        raise error
    except YandexAPICreateFolderError as error:
        message_yandex_error(chat_id, str(error))

        # it is expected error and should be
        # logged only to user
        return

    text = None

    if (last_status_code == 201):
        text = "Created"
    elif (last_status_code == 409):
        text = "Already exists"
    else:
        text = f"Unknown operation status: {last_status_code}"

    telegram.send_message(
        chat_id=chat_id,
        text=text
    )


def get_folder_name(
    telegram_message,
    route_source: RouteSource
) -> str:
    folder_name = telegram_message.get_text()

    # On "Disposable handler" route we expect pure text,
    # in other cases we expect bot command as start of a message
    if (route_source != RouteSource.DISPOSABLE_HANDLER):
        folder_name = folder_name.replace(
            CommandName.CREATE_FOLDER.value,
            "",
            1
        ).strip()

    return folder_name


def message_wait_for_text(chat_id: int) -> None:
    telegram.send_message(
        chat_id=chat_id,
        parse_mode="HTML",
        text=(
            "Send a folder name to create."
            "\n\n"
            "It should starts from root directory, "
            "nested folders should be separated with "
            '"<code>/</code>" character. '
            "In short, i expect a full path."
            "\n\n"
            "Example: <code>Telegram Bot/kittens and raccoons</code>"
        )
    )


def message_yandex_error(chat_id: int, error_text: str) -> None:
    telegram.send_message(
        chat_id=chat_id,
        text=(
            error_text or
            "Unknown Yandex.Disk error"
        )
    )
