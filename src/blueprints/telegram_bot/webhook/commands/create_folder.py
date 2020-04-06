from flask import g

from .....api import telegram, yandex
from ..decorators import (
    yd_access_token_required,
    get_db_data
)
from ..responses import (
    abort_command,
    cancel_command
)


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
    message_folder_name = message_text.replace("/create_folder", "").strip()
    folders = message_folder_name.split("/")
    absolute_path = ""
    allowed_erors = [409]

    # yandex not able to create folder if some of
    # middle folders not exists. We will try to create
    # each folder one by one, and ignore errors (if
    # already exists, for example) from all folder names
    # except last one.
    for folder in folders:
        response = None
        absolute_path = f"{absolute_path}/{folder}"

        try:
            response = yandex.create_folder(
                access_token,
                path=absolute_path
            )
        except Exception as e:
            print(e)
            return cancel_command(chat.telegram_id)

        status = response["HTTP_STATUS_CODE"]

        if (
            (status == 201) or
            (not is_error_response(response)) or
            (status in allowed_erors)
        ):
            continue

        error_text = create_error_text(response)

        return telegram.send_message(
            chat_id=chat.telegram_id,
            text=error_text
        )

    telegram.send_message(
        chat_id=chat.telegram_id,
        text="Created"
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


def is_error_response(data: dict) -> bool:
    """
    :returns: Yandex response contains error or not.
    """
    return ("error" in data)


def create_error_text(data: dict) -> str:
    """
    Constructs error text from Yandex error response.
    """
    error_name = data["error"]
    error_description = (
        data.get("message") or
        data.get("description") or
        "?"
    )

    return (
        "Yandex.Disk Error: "
        f"{error_name} ({error_description})"
    )
