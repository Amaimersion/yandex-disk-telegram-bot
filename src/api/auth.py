from requests.auth import AuthBase


class HTTPOAuthAuth(AuthBase):
    """
    Attaches HTTP OAuth Authentication to the given Request object.
    """
    def __init__(self, token: str) -> None:
        self.token = token

    def __call__(self, request: dict) -> dict:
        request.headers["Authorization"] = f"OAuth {self.token}"

        return request
