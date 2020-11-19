from time import sleep
from typing import Generator

from flask import current_app

from src.api import yandex


class YandexAPIRequestError(Exception):
    """
    Unknown error occurred during Yandex.Disk API request
    (not necessarily from Yandex).
    """
    pass


class YandexAPIError(Exception):
    """
    Error response from Yandex.Disk API.

    - may contain human-readable error message.
    """
    pass


class YandexAPICreateFolderError(Exception):
    """
    Unable to create folder on Yandex.Disk.

    - may contain human-readable error message.
    """
    pass


class YandexAPIUploadFileError(Exception):
    """
    Unable to upload folder on Yandex.Disk.

    - may contain human-readable error message.
    """
    pass


class YandexAPIPublishItemError(Exception):
    """
    Unable to pubish an item from Yandex.Disk.

    - may contain human-readable error message.
    """
    pass


class YandexAPIUnpublishItemError(Exception):
    """
    Unable to unpublish an item from Yandex.Disk.

    - may contain human-readable error message.
    """
    pass


class YandexAPIExceededNumberOfStatusChecksError(Exception):
    """
    There was too much attempts to check status
    of Yandex.Disk operation. Yandex didn't give any
    acceptable status, i.e. operation still in progress
    (most probably) and function cannot do any status
    checks because of check limit. So, operation status
    becoming unknown.
    """
    pass


def create_folder(
    user_access_token: str,
    folder_name: str
) -> int:
    """
    Creates folder using Yandex API.

    Yandex not able to create folder if some of
    middle folders not exists. This method will try to create
    each folder one by one, and ignore safe errors (if
    already exists, for example) from all folder names
    except last one.

    :returns: Last (for last folder name) HTTP Status code.

    :raises: YandexAPIRequestError
    :raises: YandexAPICreateFolderError
    """
    folders = [x for x in folder_name.split("/") if x]
    folder_path = ""
    last_status_code = 201  # root always created
    allowed_errors = [409]

    for folder in folders:
        result = None
        folder_path = f"{folder_path}/{folder}"

        try:
            result = yandex.create_folder(
                user_access_token,
                path=folder_path
            )
        except Exception as error:
            raise YandexAPIRequestError(error)

        response = result["content"]
        last_status_code = result["status_code"]

        if (
            (last_status_code == 201) or
            (last_status_code in allowed_errors) or
            (not is_error_yandex_response(response))
        ):
            continue

        raise YandexAPICreateFolderError(
            create_yandex_error_text(response)
        )

    return last_status_code


def publish_item(
    user_access_token: str,
    absolute_item_path: str
) -> None:
    """
    Publish an item that already exists on Yandex.Disk.

    :raises: YandexAPIRequestError
    :raises: YandexAPIPublishItemError
    """
    try:
        response = yandex.publish(
            user_access_token,
            path=absolute_item_path
        )
    except Exception as error:
        raise YandexAPIRequestError(error)

    response = response["content"]
    is_error = is_error_yandex_response(response)

    if (is_error):
        raise YandexAPIPublishItemError(
            create_yandex_error_text(
                response
            )
        )


def unpublish_item(
    user_access_token: str,
    absolute_item_path: str
) -> None:
    """
    Unpublish an item that already exists on Yandex.Disk.

    :raises: YandexAPIRequestError
    :raises: YandexAPIUnpublishItemError
    """
    try:
        response = yandex.unpublish(
            user_access_token,
            path=absolute_item_path
        )
    except Exception as error:
        raise YandexAPIRequestError(error)

    response = response["content"]
    is_error = is_error_yandex_response(response)

    if (is_error):
        raise YandexAPIUnpublishItemError(
            create_yandex_error_text(
                response
            )
        )


def upload_file_with_url(
    user_access_token: str,
    folder_path: str,
    file_name: str,
    download_url: str
) -> Generator[str, None, None]:
    """
    Uploads a file to Yandex.Disk using file download url.

    - before uploading creates a folder.
    - after uploading will monitor operation status according
    to app configuration. Because it is synchronous, it may
    take significant time to end this function!

    :yields: status of operation in Yandex format (for example,
    `"in progress"`). It will yields with some interval (according
    to app configuration). Order is an order in which Yandex
    sends the operation status.

    :raises: YandexAPIRequestError
    :raises: YandexAPICreateFolderError
    :raises: YandexAPIUploadFileError
    :raises: YandexAPIExceededNumberOfStatusChecksError
    """
    create_folder(
        user_access_token=user_access_token,
        folder_name=folder_path
    )

    folders = [x for x in folder_path.split("/") if x]
    full_path = "/".join(folders + [file_name])
    response = None

    try:
        response = yandex.upload_file_with_url(
            user_access_token,
            url=download_url,
            path=full_path
        )
    except Exception as error:
        raise YandexAPIRequestError(error)

    operation_status_link = response["content"]
    is_error = is_error_yandex_response(operation_status_link)

    if (is_error):
        raise YandexAPIUploadFileError(
            create_yandex_error_text(
                operation_status_link
            )
        )

    operation_status = {}
    attempt = 0
    max_attempts = current_app.config[
        "YANDEX_DISK_API_CHECK_OPERATION_STATUS_MAX_ATTEMPTS"
    ]
    interval = current_app.config[
        "YANDEX_DISK_API_CHECK_OPERATION_STATUS_INTERVAL"
    ]

    while not (
        is_error_yandex_response(operation_status) or
        yandex_operation_is_completed(operation_status) or
        attempt >= max_attempts
    ):
        sleep(interval)

        try:
            response = yandex.make_link_request(
                data=operation_status_link,
                user_token=user_access_token
            )
        except Exception as error:
            raise YandexAPIRequestError(error)

        operation_status = response["content"]

        if ("status" in operation_status):
            yield operation_status["status"]

        attempt += 1

    is_error = is_error_yandex_response(operation_status)
    is_completed = yandex_operation_is_completed(operation_status)

    if (is_error):
        raise YandexAPIUploadFileError(
            create_yandex_error_text(
                operation_status
            )
        )
    elif (
        (attempt >= max_attempts) and
        not is_completed
    ):
        raise YandexAPIExceededNumberOfStatusChecksError()


def get_disk_info(user_access_token: str) -> dict:
    """
    See for interface:
    - https://yandex.ru/dev/disk/api/reference/capacity-docpage/
    - https://dev.yandex.net/disk-polygon/#!/v147disk

    :returns: Information about user Yandex.Disk.

    :raises: YandexAPIRequestError
    """
    try:
        response = yandex.get_disk_info(user_access_token)
    except Exception as error:
        raise YandexAPIRequestError(error)

    response = response["content"]
    is_error = is_error_yandex_response(response)

    if (is_error):
        raise YandexAPIUploadFileError(
            create_yandex_error_text(
                response
            )
        )

    return response


def is_error_yandex_response(data: dict) -> bool:
    """
    :returns: Yandex response contains error or not.
    """
    return ("error" in data)


def create_yandex_error_text(data: dict) -> str:
    """
    :returns: Human error message from Yandex error response.
    """
    error_name = data.get(
        "error",
        "?"
    )
    error_description = (
        data.get("message") or
        data.get("description") or
        "?"
    )

    return (f"{error_name}: {error_description}")


def yandex_operation_is_completed(data: dict) -> bool:
    """
    :returns: Yandex response contains completed
    operation status or not.
    """
    return (
        ("status" in data) and
        (
            (data["status"] == "success") or
            # Yandex documentation is different in some places
            (data["status"] == "failure") or
            (data["status"] == "failed")
        )
    )
