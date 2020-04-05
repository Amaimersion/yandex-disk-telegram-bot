from time import sleep
from typing import Union

from flask import g, current_app

from .....api import telegram, yandex
from .....api.utils import quote
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

    user_access_token = user.yandex_disk_token.get_access_token()
    download_url = telegram.create_file_download_url(
        file["file_path"]
    )
    operation_status_link = None

    try:
        operation_status_link = yandex.upload_file_with_url(
            user_access_token,
            url=download_url,
            path=quote("disk:/" + file["file_path"])
        )
    except Exception as e:
        print(e)
        return cancel_command(chat.telegram_id)

    if (is_error_response(operation_status_link)):
        return telegram.send_message(
            chat_id=chat.telegram_id,
            text=create_error_text(operation_status_link)
        )

    track_status = True
    result = None
    attempt = 0
    max_attempts = current_app.config[
        "YANDEX_DISK_API_CHECK_OPERATION_STATUS_MAX_ATTEMPTS"
    ]
    interval = current_app.config[
        "YANDEX_DISK_API_CHECK_OPERATION_STATUS_INTERVAL"
    ]

    while (track_status):
        try:
            result = yandex.make_link_request(
                data=operation_status_link,
                user_token=user_access_token
            )
        except Exception as e:
            print(e)
            return cancel_command(chat.telegram_id)

        if ("status" in result):
            telegram.send_message(
                chat_id=chat.telegram_id,
                text=f"Status: {result['status']}"
            )

        attempt += 1

        track_status = not (
            is_error_response(result) or
            operation_is_completed(result) or
            attempt >= max_attempts
        )

        if (track_status):
            sleep(interval)

    status_text = None

    if (is_error_response(result)):
        status_text = create_error_text(result)
    elif (attempt >= max_attempts):
        status_text = (
            "I can't track operation status anymore. "
            "Perform manual checking."
        )

    # we already logged `status` in while-loop.
    if (status_text):
        telegram.send_message(
            chat_id=chat.telegram_id,
            text=status_text
        )


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
        "Error from Yandex: "
        f"{error_name} ({error_description})"
    )


def operation_is_completed(data: dict) -> bool:
    """
    Checks if Yandex response contains completed
    operation status.
    """
    return (
        ("status" in data) and
        (
            (data["status"] == "success") or
            (data["status"] == "failure")
        )
    )
