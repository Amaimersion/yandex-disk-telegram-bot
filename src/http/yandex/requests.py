from os import environ

from requests.auth import HTTPBasicAuth
from flask import current_app

from src.http.request import (
    create_url,
    request
)
from src.http.auth import HTTPOAuthAuth


def create_bot_oauth_url(method_name: str) -> str:
    """
    Creates Yandex OAuth URL for bot request.

    :param method_name: Name of API method in URL.
    """
    return create_url(
        "https://oauth.yandex.ru",
        method_name
    )


def create_user_oauth_url(state: str) -> str:
    """
    Creates Yandex OAuth URL for user request.

    - https://yandex.ru/dev/oauth/doc/dg/concepts/about-docpage/

    :param state: urlsafe `state` parameter.
    """
    client_id = environ["YANDEX_OAUTH_API_APP_ID"]

    return (
        "https://oauth.yandex.ru/authorize?"
        "response_type=code"
        f"&client_id={client_id}"
        f"&state={state}"
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
    url = create_bot_oauth_url(method_name)
    timeout = current_app.config["YANDEX_OAUTH_API_TIMEOUT"]
    id = environ["YANDEX_OAUTH_API_APP_ID"]
    password = environ["YANDEX_OAUTH_API_APP_PASSWORD"]

    return request(
        raise_for_status=False,
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
    user_token: str
):
    """
    Makes HTTP request to Yandex.Disk.

    - it will not raise in case of error HTTP code.
    - see `api/request.py` documentation for more.

    :param http_method: Name of HTTP method for request.
    :param api_method: Name of API method in URL.
    :param data: JSON data to send.
    :param user_token: User OAuth token to access the API.
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
        auth=HTTPOAuthAuth(user_token),
        allow_redirects=False,
        verify=True
    )


def make_link_request(data: dict, user_token: str):
    """
    https://yandex.ru/dev/disk/api/reference/response-objects-docpage/#link

    - it will not raise in case of error HTTP code.
    - see `api/request.py` documentation for more.

    :param data: Data of link to handle.
    :param user_token: User OAuth token to access the API.

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
        auth=HTTPOAuthAuth(user_token),
        allow_redirects=False,
        verify=True
    )


def make_photo_preview_request(photo_url: str, user_token: str):
    """
    Makes request to URL in order to get bytes content of photo.

    Yandex requires user OAuth token in order to get
    access to photo previews, so, it is why you should
    use this method.

    - it will not raise in case of error HTTP code.
    - see `api/request.py` documentation for more.

    :param photo_url:
    URL of photo.
    :param user_token:
    User OAuth token to access this URL.

    :returns:
    See `api/request.py`.
    In case of `ok = True` under `content` will be bytes content
    of requested photo.
    """
    timeout = current_app.config["YANDEX_DISK_API_TIMEOUT"]

    return request(
        raise_for_status=False,
        content_type="bytes",
        method="GET",
        url=photo_url,
        timeout=timeout,
        auth=HTTPOAuthAuth(user_token),
        allow_redirects=False,
        verify=True
    )
