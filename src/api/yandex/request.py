import os

import requests
from requests.auth import AuthBase, HTTPBasicAuth
from flask import current_app

from .exceptions import (
    InvalidResponseFormatException
)


class HTTPOAuthAuth(AuthBase):
    """
    Attaches HTTP Oauth Authentication to the given Request object.
    """
    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers["Authorization"] = f"OAuth {self.token}"

        return request


def create_oauth_url(method_name: str) -> str:
    """
    Creates Yandex OAuth URL for request.

    :param method_name: Name of API method in URL.
    """
    base_url = "https://oauth.yandex.ru"
    url = f"{base_url}/{method_name}"

    return url


def create_disk_url(method_name: str) -> str:
    """
    Creates Yandex.Disk URL for request.

    :param method_name: Name of API method in URL.
    """
    base_url = "https://cloud-api.yandex.net/v1/disk"
    url = f"{base_url}/{method_name}"

    return url


def make_oauth_request(method_name: str, data: dict) -> dict:
    """
    Makes HTTP request to Yandex OAuth.

    :param method_name: Name of API method in URL.
    :param data: Data to send.

    :raises requests.RequestException:
    https://requests.readthedocs.io/en/master/api/#exceptions
    :raises YandexOauthAPIException:
    See `exceptions.py` for documentation.
    """
    url = create_oauth_url(method_name)
    timeout = current_app.config["YANDEX_OAUTH_API_TIMEOUT"]
    id = os.getenv("YANDEX_OAUTH_API_APP_ID", "")
    password = os.getenv("YANDEX_OAUTH_API_APP_PASSWORD", "")
    response = requests.post(
        url,
        data=data,
        timeout=timeout,
        auth=HTTPBasicAuth(id, password),
        allow_redirects=False,
        verify=True
    )

    response.raise_for_status()

    response_data = {}

    try:
        response_data = response.json()
    except ValueError:
        raise InvalidResponseFormatException("Not a JSON response")

    return response_data


def make_disk_request(method_name: str, data: dict, user_token: str) -> dict:
    """
    Makes HTTP request to Yandex.Disk.

    :param method_name: Name of API method in URL.
    :param data: JSON data to send.
    :param user_token: User OAuth token to access the API.

    :raises requests.RequestException:
    https://requests.readthedocs.io/en/master/api/#exceptions
    :raises YandexOauthAPIException:
    See `exceptions.py` for documentation.
    """
    url = create_disk_url(method_name)
    timeout = current_app.config["YANDEX_DISK_API_TIMEOUT"]
    response = requests.post(
        url,
        json=data,
        timeout=timeout,
        auth=HTTPOAuthAuth(user_token),
        allow_redirects=False,
        verify=True
    )

    response.raise_for_status()

    response_data = {}

    try:
        response_data = response.json()
    except ValueError:
        raise InvalidResponseFormatException("Not a JSON response")

    return response_data
