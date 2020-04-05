from typing import Union

from flask import g

from .....api import telegram
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

    file = None

    try:
        file = telegram.get_file(
            file_id=biggest_photo["file_id"]
        )
    except Exception as e:
        print(e)
        return cancel_command(chat.telegram_id)

    download_url = telegram.create_file_download_url(
        file["file_path"]
    )

    print(download_url)


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
