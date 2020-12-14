import typing

import requests


CONTENT_TYPE = typing.Literal[
    "none",
    "bytes",
    "json",
    "text"
]


class RequestResult(typing.TypedDict):
    # https://requests.readthedocs.io/en/master/api/#requests.Response.ok
    ok: bool
    # https://requests.readthedocs.io/en/master/api/#requests.Response.reason
    reason: str
    # https://requests.readthedocs.io/en/master/api/#requests.Response.status_code
    status_code: int
    # Depends on `content_type` argument
    content: typing.Any


def request(
    raise_for_status=False,
    content_type: CONTENT_TYPE = "none",
    **kwargs
) -> RequestResult:
    """
    Makes HTTP request.

    :param raise_for_status:
    Raises exception if response code is 400 <= x < 600.
    :param content_type:
    How to decode response content.
    :param **kwargs:
    See https://requests.readthedocs.io/en/master/api/#requests.request

    :returns:
    Result of request.
    See `RequestResult` documentation for more.

    :raises ValueError:
    If required content_type is `json` and response
    body does not contain valid json.
    :raises requests.RequestException:
    https://requests.readthedocs.io/en/master/api/#exceptions
    """
    response = requests.request(**kwargs)

    if (raise_for_status):
        response.raise_for_status()

    content = {
        "none": lambda: None,
        "bytes": lambda: response.content,
        "json": lambda: response.json(),
        "text": lambda: response.text
    }
    result: RequestResult = {
        "ok": response.ok,
        "reason": response.reason,
        "status_code": response.status_code,
        "content": content[content_type]()
    }

    return result


def create_url(*args: str) -> str:
    """
    Creates URL for HTTP request.

    - doesn't contains trailing slash at the end.

    :param *args: Segments to join. Order will be saved.

    :returns: Created URL.
    """
    separator = "/"

    return separator.join(
        [x[:-1] if x.endswith(separator) else x for x in args]
    )
