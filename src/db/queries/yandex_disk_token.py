from src.db import YandexDiskToken


def delete_all_yd_tokens() -> int:
    """
    Deletes all Y.D. tokens from a table.

    You have to commit DB changes!

    :returns: Count of deleted Y.D. tokens.
    """
    return YandexDiskToken.query.delete()
