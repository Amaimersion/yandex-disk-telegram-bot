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
    """
    return make_disk_request("resources/upload", kwargs, user_token)
