from typing import Union

from flask import g, current_app

from .....api import telegram
from .common.decorators import (
    yd_access_token_required,
    get_db_data
)
from .common.responses import (
    abort_command,
    cancel_command
)
from .common.api import (
    upload_file_with_url,
    YandexAPIRequestError,
    YandexAPICreateFolderError,
    YandexAPIUploadFileError,
    YandexAPIExceededNumberOfStatusChecksError
)


@yd_access_token_required
@get_db_data
def handle():
    """
    Handles `/upload_file` command.
    """
    message = g.incoming_message
    user = g.db_user
    chat = g.db_incoming_chat

    if (not message_is_valid(message)):
        return abort_command(chat.telegram_id)

    try:
        file = telegram.send_chat_action(
            chat_id=chat.telegram_id,
            action="upload_document"
        )
    except Exception as e:
        print(e)
        return cancel_command(chat.telegram_id)

    document = get_document(message)
    file = None

    try:
        file = telegram.get_file(
            file_id=document["file_id"]
        )
    except Exception as e:
        print(e)
        return cancel_command(chat.telegram_id)

    user_access_token = user.yandex_disk_token.get_access_token()
    folder_path = current_app.config[
        "YANDEX_DISK_API_DEFAULT_UPLOAD_FOLDER"
    ]
    file_name = document.get("file_name") or file["file_unique_id"]
    download_url = telegram.create_file_download_url(
        file["file_path"]
    )

    try:
        for status in upload_file_with_url(
            access_token=user_access_token,
            folder_path=folder_path,
            file_name=file_name,
            download_url=download_url
        ):
            telegram.send_message(
                chat_id=chat.telegram_id,
                text=f"Status: {status}"
            )
    except YandexAPICreateFolderError as error:
        error_text = str(error) or (
            "I can't create default upload folder "
            "due to an unknown Yandex error."
        )

        return telegram.send_message(
            chat_id=chat.telegram_id,
            text=error_text
        )
    except YandexAPIUploadFileError as error:
        error_text = str(error) or (
            "I can't upload this file "
            "due to an unknown Yandex error."
        )

        return telegram.send_message(
            chat_id=chat.telegram_id,
            reply_to_message_id=message["message_id"],
            text=error_text
        )
    except YandexAPIExceededNumberOfStatusChecksError:
        error_text = (
            "I can't track operation status anymore. "
            "Perform manual checking."
        )

        return telegram.send_message(
            chat_id=chat.telegram_id,
            reply_to_message_id=message["message_id"],
            text=error_text
        )
    except (YandexAPIRequestError, Exception) as error:
        print(error)
        return cancel_command(chat.telegram_id)


def message_is_valid(message: dict) -> bool:
    """
    :returns: Telegram message is valid.
    """
    return (
        isinstance(
            message.get("document"),
            dict
        )
    )


def get_document(message: dict) -> dict:
    """
    :returns: User Telegram document.
    """
    return message["document"]