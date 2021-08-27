from time import sleep
from typing import Generator, Deque
from collections import deque

from flask import current_app

from src.http import yandex
from src.i18n import gettext


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


class YandexDiskPath:
    """
    Yandex.Disk path to resource.

    - you should use this class, not raw strings from user!
    """
    def __init__(self, *args):
        """
        :param *args:
        List of raw paths from user.
        """
        self.separator = "/"
        self.disk_namespace = "disk:"
        self.trash_namespace = "trash:"
        self.raw_paths = args

    def __repr__(self) -> str:
        """
        :returns:
        Debug representation.
        """
        return self.create_absolute_path()

    def get_absolute_path(self) -> Deque[str]:
        """
        :returns:
        Iterable of resource names without separator.
        Join result with separator will be a valid Yandex.Disk path.

        :examples:
        1) `self.raw_paths = ["Telegram Bot/test", "name.jpg"]` ->
        `["disk:", "Telegram Bot", "test", "name.jpg"]`.
        2) `self.raw_paths = ["disk:/Telegram Bot//test", "/name.jpg/"]` ->
        `["disk:", "Telegram Bot", "test", "name.jpg"]`.
        """
        data = deque()

        for raw_path in self.raw_paths:
            data.extend(
                [x for x in raw_path.split(self.separator) if x]
            )

        if not data:
            data.append(self.disk_namespace)

        namespace = data[0]
        is_valid_namepsace = namespace in (
            self.disk_namespace,
            self.trash_namespace
        )

        # Yandex.Disk path must starts with some namespace
        # (Disk, Trash, etc.). Paths without valid namespace
        # are invalid! However, they can work without namespace.
        # But paths without namespace can lead to unexpected
        # error at any time. So, you always should add namespace.
        # For example, `Telegram Bot/12` will work, but
        # `Telegram Bot/12:12` will lead to `DiskPathFormatError`
        # from Yandex because Yandex assumes `12` as namespace.
        # `disk:/Telegram Bot/12:12` will work fine.
        if not is_valid_namepsace:
            # Let's use Disk namespace by default
            data.appendleft(self.disk_namespace)

        return data

    def create_absolute_path(self) -> str:
        """
        :returns:
        Valid absolute path.
        """
        data = self.get_absolute_path()

        # if path is only namespace, then
        # it should end with separator,
        # otherwise there should be no
        # separator at the end
        if (len(data) == 1):
            return f"{data.pop()}{self.separator}"
        else:
            return self.separator.join(data)

    def generate_absolute_path(
        self,
        include_namespace=True
    ) -> Generator[str, None, None]:
        """
        :yields:
        Valid absolute path piece by piece.

        :examples:
        1) `create_absolute_path()` -> `disk:/Telegram Bot/folder/file.jpg`
        `generate_absolute_path(True)` -> `[disk:/, disk:/Telegram Bot,
        disk:/Telegram Bot/folder, disk:/Telegram Bot/folder/file.jpg]`.
        """
        data = self.get_absolute_path()
        absolute_path = data.popleft()

        if include_namespace:
            yield f"{absolute_path}{self.separator}"

        for element in data:
            absolute_path += f"{self.separator}{element}"
            yield absolute_path


def create_yandex_error_text(data: dict) -> str:
    """
    :returns:
    Human error message from Yandex error response.
    """
    error_name = data.get("error")
    error_description = (
        data.get("message") or
        data.get("description")
    )

    if not error_name:
        current_app.logger.warning(
            f"Error name is unknown: {data}"
        )
        error_name = "?"

    if not error_description:
        current_app.logger.warning(
            f"Error description is unknown: {data}"
        )
        error_description = "?"

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


def yandex_operation_is_in_progress(data: dict) -> bool:
    """
    :returns:
    Yandex response contains status which
    indicates that operation is in progress.
    """
    return (
        ("status" in data) and
        (data["status"] == "in-progress")
    )


def get_yandex_operation_text(data: dict) -> str:
    """
    :param data:
    Yandex response which contains
    data about operation status.

    :returns:
    Text status of Yandex operation which
    can be used to display to user.
    """
    if yandex_operation_is_success(data):
        return gettext("success")
    elif yandex_operation_is_in_progress(data):
        return gettext("in progress")
    elif yandex_operation_is_failed(data):
        return gettext("failed")

    current_app.logger.warning(
        f"Unknown operation status: {data}"
    )

    return data.get(
        "status",
        gettext("unknown")
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
    path = YandexDiskPath(folder_name)
    resources = path.generate_absolute_path(True)
    last_status_code = 201  # namespace always created
    allowed_errors = [409]

    current_app.logger.debug(
        f"{folder_name} was converted to {path}"
    )

    for resource in resources:
        result = None

        try:
            result = yandex.create_folder(
                user_access_token,
                path=resource
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
    path = YandexDiskPath(absolute_item_path)
    absolute_path = path.create_absolute_path()

    current_app.logger.debug(
        f"{absolute_item_path} was converted to {absolute_path}"
    )

    try:
        response = yandex.publish(
            user_access_token,
            path=absolute_path
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
    path = YandexDiskPath(absolute_item_path)
    absolute_path = path.create_absolute_path()

    current_app.logger.debug(
        f"{absolute_item_path} was converted to {absolute_path}"
    )

    try:
        response = yandex.unpublish(
            user_access_token,
            path=absolute_path
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

    path = YandexDiskPath(folder_path, file_name)
    absolute_path = path.create_absolute_path()
    response = None

    current_app.logger.debug(
        f"Download URL: {download_url}"
    )
    current_app.logger.debug(
        f"Final path: {absolute_path}"
    )

    try:
        response = yandex.upload_file_with_url(
            user_access_token,
            url=download_url,
            path=absolute_path
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
        operation_status_text = get_yandex_operation_text(operation_status)
        attempt += 1
        too_many_attempts = (attempt >= max_attempts)

        if not is_error:
            yield {
                "success": is_success,
                "failed": is_failed,
                "completed": (is_success or is_failed),
                "status": operation_status_text
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
    path = YandexDiskPath(absolute_element_path)
    absolute_path = path.create_absolute_path()

    current_app.logger.debug(
        f"{absolute_element_path} was converted to {absolute_path}"
    )

    try:
        response = yandex.get_element_info(
            user_access_token,
            path=absolute_path,
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
