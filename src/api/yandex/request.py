import os

import requests
from requests.auth import AuthBase, HTTPBasicAuth
from flask import current_app

from .exceptions import (
    InvalidResponseFormatException,
    DataConflictException
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


def make_disk_request(
    http_method: str,
    api_method: str,
    data: dict,
    token: str
) -> dict:
    """
    Makes HTTP request to Yandex.Disk.

    - it will not raise if status is not 2xx!
    - adds `HTTP_STATUS_CODE` key in response data.

    :param http_method: Name of HTTP method for request.
    :param api_method: Name of API method in URL.
    :param data: JSON data to send.
    :param token: OAuth token to access the API.

    :raises requests.RequestException:
    https://requests.readthedocs.io/en/master/api/#exceptions
    :raises YandexOauthAPIException:
    See `exceptions.py` for documentation.
    """
    url = create_disk_url(api_method)
    timeout = current_app.config["YANDEX_DISK_API_TIMEOUT"]
    response = requests.request(
        http_method.upper(),
        url,
        params=data,
        timeout=timeout,
        auth=HTTPOAuthAuth(token),
        allow_redirects=False,
        verify=True
    )
    response_data = {}
    http_code_key = "HTTP_STATUS_CODE"

    try:
        response_data = response.json()
    except ValueError:
        raise InvalidResponseFormatException("Not a JSON response")

    if (http_code_key in response_data):
        raise DataConflictException("Special key for HTTP Code already exists")

    response_data[http_code_key] = response.status_code

    return response_data


def make_link_request(data: dict, user_token: str) -> dict:
    """
    https://yandex.ru/dev/disk/api/reference/response-objects-docpage/#link
    """
    if (data["templated"]):
        raise NotImplementedError("Templating not implemented")

    timeout = current_app.config["YANDEX_DISK_API_TIMEOUT"]
    url = data["href"]
    method = data["method"].upper()
    response = requests.request(
        method,
        url,
        timeout=timeout,
        auth=HTTPOAuthAuth(user_token),
        allow_redirects=False,
        verify=True
    )
    response_data = {}

    try:
        response_data = response.json()
    except ValueError:
        raise InvalidResponseFormatException("Not a JSON response")

    return response_data
