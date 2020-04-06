import requests

from .request import make_oauth_request, make_disk_request
from .exceptions import YandexOauthAPIException


def get_access_token(**kwargs) -> dict:
    """
    https://yandex.ru/dev/oauth/doc/dg/reference/auto-code-client-docpage/#auto-code-client__get-token
    """
    return make_oauth_request("token", kwargs)


def upload_file_with_url(user_token, **kwargs) -> dict:
    """
    https://yandex.ru/dev/disk/api/reference/upload-ext-docpage/

    - adds `HTTP_STATUS_CODE` key in response data.
    """
    return make_disk_request(
        http_method="POST",
        api_method="resources/upload",
        data=kwargs,
        token=user_token
    )


def create_folder(user_token, **kwargs) -> dict:
    """
    https://yandex.ru/dev/disk/api/reference/create-folder-docpage/

    - adds `HTTP_STATUS_CODE` key in response data.
    """
    return make_disk_request(
        http_method="PUT",
        api_method="resources",
        data=kwargs,
        token=user_token
    )
