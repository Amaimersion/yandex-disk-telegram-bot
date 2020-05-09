from flask import g

from src.api import telegram
from .common.responses import (
    cancel_command,
    abort_command
)
from .common.decorators import (
    yd_access_token_required,
    get_db_data
)
from .common.yandex_api import (
    create_folder,
    YandexAPICreateFolderError,
    YandexAPIRequestError
)
from . import CommandsNames


@yd_access_token_required
@get_db_data
def handle():
    """
    Handles `/create_folder` command.
    """
    message = g.telegram_message
    user = g.db_user
    chat = g.db_chat
    message_text = message.get_text()
    folder_name = message_text.replace(
        CommandsNames.CREATE_FOLDER.value,
        ""
    ).strip()

    if not (folder_name):
        return abort_command(chat.telegram_id)

    access_token = user.yandex_disk_token.get_access_token()
    last_status_code = None

    try:
        last_status_code = create_folder(
            user_access_token=access_token,
            folder_name=folder_name
        )
    except YandexAPIRequestError as error:
        print(error)
        return cancel_command(chat.telegram_id)
    except YandexAPICreateFolderError as error:
        error_text = (
            str(error) or
            "Unknown Yandex.Disk error"
        )

        telegram.send_message(
            chat_id=chat.telegram_id,
            text=error_text
        )

        return

    text = None

    if (last_status_code == 201):
        text = "Created"
    elif (last_status_code == 409):
        text = "Already exists"
    else:
        text = f"Unknown status code: {last_status_code}"

    telegram.send_message(
        chat_id=chat.telegram_id,
        text=text
    )
