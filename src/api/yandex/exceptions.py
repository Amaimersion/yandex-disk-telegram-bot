class YandexOauthAPIException(Exception):
    """
    Expected exception that occurred while handling Yandex Oauth request.
    """
    pass


class InvalidResponseFormatException(YandexOauthAPIException):
    """
    Format of response differ from Yandex Oauth response.
    """
    pass


class DataConflictException(YandexOauthAPIException):
    """
    Response data conflicts with internal operations.
    """
    pass
