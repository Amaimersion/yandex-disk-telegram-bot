class TelegramApiException(Exception):
    """
    Expected exception that occurred while handling Telegram API request.
    """
    pass


class InvalidResponseFormatException(TelegramApiException):
    """
    Format of response differ from Telegram response.
    """
    pass


class MethodExecutionFailedException(TelegramApiException):
    """
    Telegram successfully called a method, but it failed to end.
    """
    pass
