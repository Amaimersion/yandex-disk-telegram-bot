class InvalidCredentials(Exception):
    """
    Provided credentials is not valid.
    """
    pass


class LinkExpired(Exception):
    """
    Link is expired and not valid anymore.
    """
    pass


class InvalidInsertToken(Exception):
    """
    Provided `insert_token` is not valid with
    `insert_token` from DB.
    """
    pass
