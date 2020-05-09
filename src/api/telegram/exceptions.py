class TelegramBotApiException(Exception):
    """
    Expected exception that occurred while
    handling Telegram Bot API request.
    """
    pass


class RequestFailed(TelegramBotApiException):
    """
    Telegram indicates that some error occurred
    because of something (see error message).
    """
    pass
