from flask import g

from src.api import telegram
from .common.responses import (
    cancel_command
)
from .common.decorators import (
    yd_access_token_required,
    get_db_data
)
from .common.api import (
    create_folder,
    YandexAPICreateFolderError,
    YandexAPIRequestError
)
from .common.names import CommandNames


@yd_access_token_required
@get_db_data
def handle():
    """
    Handles `/create_folder` command.
    """
    message = g.incoming_message
    user = g.db_user
    chat = g.db_incoming_chat
    access_token = user.yandex_disk_token.get_access_token()
    message_text = get_text(message)
    message_folder_name = message_text.replace(
        CommandNames.CREATE_FOLDER.value,
        ""
    ).strip()
    last_status_code = None

    try:
        last_status_code = create_folder(
            access_token=access_token,
            folder_name=message_folder_name
        )
    except YandexAPIRequestError as e:
        print(e)
        return cancel_command(chat.telegram_id)
    except YandexAPICreateFolderError as e:
        error_text = "Yandex.Disk Error"

        if hasattr(e, "message"):
            error_text = e.message

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


def get_text(message: dict) -> str:
    """
    Extracts text from a message.
    """
    return (
        message.get("text") or
        message.get("caption") or
        ""
    )
