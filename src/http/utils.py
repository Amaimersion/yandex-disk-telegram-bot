from requests.utils import quote as requests_quote


def quote(string: str) -> str:
    """
    Changes string to URL-format.

    i.e., `/test` -> `%2Ftest`.
    """
    return requests_quote(string, safe="")
