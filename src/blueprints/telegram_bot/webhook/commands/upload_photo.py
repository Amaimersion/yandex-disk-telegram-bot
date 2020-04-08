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
    Handles `/upload_photo` command.
    """
    message = g.incoming_message
    user = g.db_user
    chat = g.db_incoming_chat

    if (not message_is_valid(message)):
        return abort_command(chat.telegram_id)

    biggest_photo = get_biggest_photo(message)

    if (biggest_photo is None):
        return abort_command(chat.telegram_id)

    try:
        file = telegram.send_chat_action(
            chat_id=chat.telegram_id,
            action="upload_photo"
        )
    except Exception as e:
        print(e)
        return cancel_command(chat.telegram_id)

    file = None

    try:
        file = telegram.get_file(
            file_id=biggest_photo["file_id"]
        )
    except Exception as e:
        print(e)
        return cancel_command(chat.telegram_id)

    user_access_token = user.yandex_disk_token.get_access_token()
    folder_path = current_app.config[
        "YANDEX_DISK_API_DEFAULT_UPLOAD_FOLDER"
    ]
    file_name = file["file_unique_id"]
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
    except YandexAPIRequestError as error:
        print(error)
        return cancel_command(chat.telegram_id)
    except YandexAPICreateFolderError as error:
        error_text = "I can't create default upload folder"

        if hasattr(error, "message"):
            error_text = error.message

        return telegram.send_message(
            chat_id=chat.telegram_id,
            text=error_text
        )
    except YandexAPIUploadFileError as error:
        error_text = "I can't upload this photo"

        if hasattr(error, "message"):
            error_text = error.message

        return telegram.send_message(
            chat_id=chat.telegram_id,
            text=error_text
        )
    except YandexAPIExceededNumberOfStatusChecksError:
        error_text = (
            "I can't track operation status anymore. "
            "Perform manual checking."
        )

        return telegram.send_message(
            chat_id=chat.telegram_id,
            text=error_text
        )
    except Exception as error:
        print(error)
        return cancel_command(chat.telegram_id)


def message_is_valid(message: dict) -> bool:
    """
    :returns: Telegram message is valid.
    """
    return (
        isinstance(
            message.get("photo"),
            list
        ) and
        len(message["photo"]) > 0
    )


def photo_is_valid(photo: dict) -> bool:
    """
    :returns: Telegram photo object is valid.
    """
    return (
        isinstance(
            photo.get("file_id"),
            str
        ) and
        isinstance(
            photo.get("file_unique_id"),
            str
        ) and
        isinstance(
            photo.get("width"),
            int
        ) and
        isinstance(
            photo.get("height"),
            int
        )
    )


def get_biggest_photo(message: dict) -> Union[dict, None]:
    """
    :returns: photo with highest size among all photos.
    """
    biggest_photo = None

    for current_photo in message["photo"]:
        if (not photo_is_valid(current_photo)):
            continue

        if (
            (biggest_photo is None) or
            (current_photo["height"] > biggest_photo["height"])
        ):
            biggest_photo = current_photo

    return biggest_photo
