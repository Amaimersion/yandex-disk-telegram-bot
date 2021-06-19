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
    stateful_chat_is_enabled,
    set_disposable_handler
)
from src.blueprints.telegram_bot.webhook.dispatcher_interface import (
    DispatcherEvent
)
from ._common.responses import (
    cancel_command,
    send_yandex_disk_error,
    request_absolute_folder_name
)
from ._common.decorators import (
    yd_access_token_required
)
from ._common.utils import extract_absolute_path


@yd_access_token_required
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
    folder_name = extract_absolute_path(
        message,
        CommandName.CREATE_FOLDER.value,
        kwargs.get("route_source")
    )

    if not folder_name:
        if stateful_chat_is_enabled():
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

        return request_absolute_folder_name(chat_id)

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
        send_yandex_disk_error(chat_id, str(error))

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
