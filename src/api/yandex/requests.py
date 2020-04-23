from os import environ

from requests.auth import HTTPBasicAuth
from flask import current_app

from src.api.request import (
    create_url,
    request
)
from src.api.auth import HTTPOAuthAuth


def create_oauth_url(method_name: str) -> str:
    """
    Creates Yandex OAuth URL for request.

    :param method_name: Name of API method in URL.
    """
    return create_url(
        "https://oauth.yandex.ru",
        method_name
    )


def create_disk_url(method_name: str) -> str:
    """
    Creates Yandex.Disk URL for request.

    :param method_name: Name of API method in URL.
    """
    return create_url(
        "https://cloud-api.yandex.net/v1/disk",
        method_name
    )


def make_oauth_request(method_name: str, data: dict):
    """
    Makes HTTP request to Yandex OAuth.

    - see `api/request.py` documentation for more.

    :param method_name: Name of API method in URL.
    :param data: Data to send.
    """
    url = create_oauth_url(method_name)
    timeout = current_app.config["YANDEX_OAUTH_API_TIMEOUT"]
    id = environ["YANDEX_OAUTH_API_APP_ID"]
    password = environ["YANDEX_OAUTH_API_APP_PASSWORD"]

    return request(
        content_type="json",
        method="POST",
        url=url,
        data=data,
        timeout=timeout,
        auth=HTTPBasicAuth(id, password),
        allow_redirects=False,
        verify=True
    )


def make_disk_request(
    http_method: str,
    api_method: str,
    data: dict,
    token: str
):
    """
    Makes HTTP request to Yandex.Disk.

    - it will not raise in case of error HTTP code.
    - see `api/request.py` documentation for more.

    :param http_method: Name of HTTP method for request.
    :param api_method: Name of API method in URL.
    :param data: JSON data to send.
    :param token: OAuth token to access the API.
    """
    url = create_disk_url(api_method)
    timeout = current_app.config["YANDEX_DISK_API_TIMEOUT"]

    return request(
        raise_for_status=False,
        content_type="json",
        method=http_method.upper(),
        url=url,
        params=data,
        timeout=timeout,
        auth=HTTPOAuthAuth(token),
        allow_redirects=False,
        verify=True
    )


def make_link_request(data: dict, token: str):
    """
    https://yandex.ru/dev/disk/api/reference/response-objects-docpage/#link

    - it will not raise in case of error HTTP code.
    - see `api/request.py` documentation for more.

    :param data: Data of link to handle.
    :param token: OAuth token to access the API.

    :raises NotImplementedError: If link requires templating.
    """
    if (data["templated"]):
        raise NotImplementedError("Templating not implemented")

    url = data["href"]
    method = data["method"].upper()
    timeout = current_app.config["YANDEX_DISK_API_TIMEOUT"]

    return request(
        raise_for_status=False,
        content_type="json",
        method=method,
        url=url,
        timeout=timeout,
        auth=HTTPOAuthAuth(token),
        allow_redirects=False,
        verify=True
    )
