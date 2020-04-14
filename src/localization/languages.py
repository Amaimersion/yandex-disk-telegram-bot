from enum import IntEnum, unique


@unique
class SupportedLanguages(IntEnum):
    """
    Languages supported by app.
    """
    EN = 1
