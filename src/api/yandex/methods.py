import requests

from .request import make_oauth_request
from .exceptions import YandexOauthAPIException


def get_access_token(**kwargs) -> dict:
    """
    https://yandex.ru/dev/oauth/doc/dg/reference/auto-code-client-docpage/#auto-code-client__get-token
    """
    return make_oauth_request("token", kwargs)
