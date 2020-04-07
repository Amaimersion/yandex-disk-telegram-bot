from ......api import yandex


class YandexAPIRequestError(Exception):
    """
    Some error occurred during Yandex.Disk API request.
    """
    pass


class YandexAPIError(Exception):
    """
    Error response from Yandex.Disk API.
    """
    pass


def create_folder(access_token: str, folder_name: str) -> int:
    """
    Creates folder using Yandex API.

    Yandex not able to create folder if some of
    middle folders not exists. This method will try to create
    each folder one by one, and ignore safe errors (if
    already exists, for example) from all folder names
    except last one.

    :returns: Last (for last folder name) HTTP Status code.

    :raises: YandexAPIRequestError
    :raises: YandexAPIError
    """
    folders = [x for x in folder_name.split("/") if x]
    folder_path = ""
    last_status_code = 201  # root always created
    allowed_errors = [409]

    for folder in folders:
        response = None
        folder_path = f"{folder_path}/{folder}"

        try:
            response = yandex.create_folder(
                access_token,
                path=folder_path
            )
        except Exception as e:
            raise YandexAPIRequestError(e)

        last_status_code = response["HTTP_STATUS_CODE"]

        if (
            (last_status_code == 201) or
            (not is_error_yandex_response(response)) or
            (last_status_code in allowed_errors)
        ):
            continue

        raise YandexAPIError(
            create_yandex_error_text(response)
        )

    return last_status_code


def is_error_yandex_response(data: dict) -> bool:
    """
    :returns: Yandex response contains error or not.
    """
    return ("error" in data)


def create_yandex_error_text(data: dict) -> str:
    """
    :returns: Human error message from Yandex error response.
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
