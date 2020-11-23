from time import sleep
from typing import Generator

from flask import current_app

from src.api import yandex


# region Exceptions


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
    Unable to upload file on Yandex.Disk.

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


class YandexAPIGetElementInfoError(Exception):
    """
    Unable to get information about Yandex.Disk
    element (folder or file).

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


# endregion


# region Helpers


def create_yandex_error_text(data: dict) -> str:
    """
    :returns:
    Human error message from Yandex error response.
    """
    error_name = data.get("error", "?")
    error_description = (
        data.get("message") or
        data.get("description") or
        "?"
    )

    return (f"{error_name}: {error_description}")


def is_error_yandex_response(data: dict) -> bool:
    """
    :returns: Yandex response contains error or not.
    """
    return ("error" in data)


def yandex_operation_is_success(data: dict) -> bool:
    """
    :returns:
    Yandex response contains status which
    indicates that operation is successfully ended.
    """
    return (
        ("status" in data) and
        (data["status"] == "success")
    )


def yandex_operation_is_failed(data: dict) -> bool:
    """
    :returns:
    Yandex response contains status which
    indicates that operation is failed.
    """
    return (
        ("status" in data) and
        (data["status"] in (
            # Yandex documentation is different in some places
            "failure",
            "failed"
        ))
    )


# endregion


# region API


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

    :returns:
    Last (for last folder name) HTTP Status code.

    :raises:
    `YandexAPIRequestError`,
    `YandexAPICreateFolderError`.
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
            not is_error_yandex_response(response)
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

    :raises:
    `YandexAPIRequestError`,
    `YandexAPIPublishItemError`.
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

    if is_error:
        raise YandexAPIPublishItemError(
            create_yandex_error_text(response)
        )


def unpublish_item(
    user_access_token: str,
    absolute_item_path: str
) -> None:
    """
    Unpublish an item that already exists on Yandex.Disk.

    :raises:
    `YandexAPIRequestError`,
    `YandexAPIUnpublishItemError`.
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

    if is_error:
        raise YandexAPIUnpublishItemError(
            create_yandex_error_text(response)
        )


def upload_file_with_url(
    user_access_token: str,
    folder_path: str,
    file_name: str,
    download_url: str
) -> Generator[dict, None, None]:
    """
    Uploads a file to Yandex.Disk using file download url.

    - before uploading creates a folder.
    - after uploading will monitor operation status according
    to app configuration. Because it is synchronous, it may
    take significant time to end this function!

    :yields:
    `dict` with `success`, `failed`, `completed`, `status`.
    It will yields with some interval (according
    to app configuration). Order is an order in which
    Yandex sent an operation status, so, `status` can
    be safely logged to user.
    `status` - currenet string status of uploading
    (for example, `in progress`).
    `completed` - uploading is completed.
    `success` - uploading is successfully ended.
    `failed` - uploading is failed (unknown error, known
    error will be throwed with `YandexAPIUploadFileError`).

    :raises:
    `YandexAPIRequestError`,
    `YandexAPICreateFolderError`,
    `YandexAPIUploadFileError`,
    `YandexAPIExceededNumberOfStatusChecksError`
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

    if is_error:
        raise YandexAPIUploadFileError(
            create_yandex_error_text(operation_status_link)
        )

    operation_status = None
    is_error = False
    is_success = False
    is_failed = False
    is_completed = False
    attempt = 0
    max_attempts = current_app.config[
        "YANDEX_DISK_API_CHECK_OPERATION_STATUS_MAX_ATTEMPTS"
    ]
    interval = current_app.config[
        "YANDEX_DISK_API_CHECK_OPERATION_STATUS_INTERVAL"
    ]
    too_many_attempts = (attempt >= max_attempts)

    while not (
        is_error or
        is_completed or
        too_many_attempts
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
        is_error = is_error_yandex_response(operation_status)
        is_success = yandex_operation_is_success(operation_status)
        is_failed = yandex_operation_is_failed(operation_status)
        is_completed = (is_success or is_failed)
        attempt += 1
        too_many_attempts = (attempt >= max_attempts)

        if not is_error:
            yield {
                "success": is_success,
                "failed": is_failed,
                "completed": (is_success or is_failed),
                "status": operation_status.get(
                    "status",
                    "unknown"
                )
            }

    if is_error:
        raise YandexAPIUploadFileError(
            create_yandex_error_text(operation_status)
        )
    elif (
        too_many_attempts and
        not is_completed
    ):
        raise YandexAPIExceededNumberOfStatusChecksError()


def get_disk_info(user_access_token: str) -> dict:
    """
    See for interface:
    - https://yandex.ru/dev/disk/api/reference/capacity-docpage/
    - https://dev.yandex.net/disk-polygon/#!/v147disk

    :returns:
    Information about user Yandex.Disk.

    :raises:
    `YandexAPIRequestError`.
    """
    try:
        response = yandex.get_disk_info(user_access_token)
    except Exception as error:
        raise YandexAPIRequestError(error)

    response = response["content"]
    is_error = is_error_yandex_response(response)

    if is_error:
        raise YandexAPIUploadFileError(
            create_yandex_error_text(response)
        )

    return response


def get_element_info(
    user_access_token: str,
    absolute_element_path: str,
    get_public_info=False,
    preview_size="L",
    preview_crop=False,
    embedded_elements_limit=0,
    embedded_elements_offset=0,
    embedded_elements_sort="name"
) -> dict:
    """
    - https://yandex.ru/dev/disk/api/reference/meta.html
    - https://dev.yandex.net/disk-polygon/?lang=ru&tld=ru#!/v147disk47public47resources/GetPublicResource # noqa

    :param user_access_token:
    User access token.
    :param absolute_element_path:
    Absolute path of element.
    :param get_public_info:
    Make another HTTP request to get public info.
    If `True`, then these fields will be added in
    normal info: `views_count`, `owner`.
    Set to `False` if you don't need this information -
    this will improve speed.
    :param preview_size:
    Size of preview (if available).
    :param preview_crop:
    Allow cropping of preview.
    :param embedded_elements_limit:
    How many embedded elements (elements inside
    folder) should be included in response.
    Set to `0` if you don't need this information -
    this will improve speed.
    :param embedded_elements_offset:
    Offset for embedded elements.
    Note `sort` parameter.
    :param embedded_elements_sort:
    How to sort embedded elements.
    Possible values: `name`, `path`, `created`,
    `modified`, `size`. Append `-` for reverse
    order (example: `-name`).

    :returns:
    Information about object.
    Check for keys before using them!

    :raises:
    `YandexAPIRequestError`, `YandexAPIGetElementInfoError`.
    """
    try:
        response = yandex.get_element_info(
            user_access_token,
            path=absolute_element_path,
            preview_crop=preview_crop,
            preview_size=preview_size,
            limit=embedded_elements_limit,
            offset=embedded_elements_offset,
            sort=embedded_elements_sort
        )
    except Exception as error:
        raise YandexAPIRequestError(error)

    response = response["content"]
    is_error = is_error_yandex_response(response)

    if is_error:
        raise YandexAPIGetElementInfoError(
            create_yandex_error_text(response)
        )

    if (
        get_public_info and
        ("public_key" in response)
    ):
        public_info_response = None

        try:
            public_info_response = yandex.get_element_public_info(
                user_access_token,
                public_key=response["public_key"],
                # we need only these fields, because they
                # are missing in normal info
                fields="views_count,owner",
                preview_crop=preview_crop,
                preview_size=preview_size,
                limit=embedded_elements_limit,
                offset=embedded_elements_offset,
                sort=embedded_elements_sort
            )
        except Exception as error:
            raise YandexAPIRequestError(error)

        public_info_response = public_info_response["content"]
        is_error = is_error_yandex_response(public_info_response)

        if is_error:
            raise YandexAPIGetElementInfoError(
                create_yandex_error_text(response)
            )

        response = {**response, **public_info_response}

    return response


# endregion
