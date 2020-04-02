from typing import List, Union, NewType

from sqlalchemy.sql.expression import func

from .. import User, YandexDiskToken


UserOrNone = NewType("UserOrNone", Union[User, None])


def get_users_count() -> int:
    """
    Returns number of users.
    """
    return User.query.count()


def get_random_user() -> UserOrNone:
    """
    Returns random user.
    """
    return User.query.order_by(func.random()).first()


def get_user_by_id(id: int) -> UserOrNone:
    """
    Returns user with specified id.
    """
    return User.query.filter(User.id == id).first()


def get_user_by_telegram_id(telegram_id: int) -> UserOrNone:
    """
    Returns user with specified telegram id.
    """
    return User.query.filter(User.telegram_id == telegram_id).first()


def _get_query_all_users_without_yd_token():
    """
    Returns query for all users which doesn't have Yandex.Disk token
    (either "pending" token or "received" token).
    """
    subquery = ~User.query.filter(User.id == YandexDiskToken.user_id).exists()
    query = User.query.filter(subquery)

    return query


def get_users_without_yd_token_count() -> int:
    """
    Returns count of users which doesn't have Yandex.Disk token
    (either "pending" token or "received" token).
    """
    query = _get_query_all_users_without_yd_token()

    return query.count()


def get_all_users_without_yd_token() -> List[UserOrNone]:
    """
    Returns all users which doesn't have Yandex.Disk token
    (either "pending" token or "received" token).
    """
    query = _get_query_all_users_without_yd_token()

    return query.all()


def get_random_user_without_yd_token() -> UserOrNone:
    """
    Returns random user which doesn't have Yandex.Disk token
    (either "pending" token or "received" token).
    """
    query = _get_query_all_users_without_yd_token()

    return query.order_by(func.random()).first()


def delete_all_users() -> int:
    """
    Deletes all users from a table.

    You have to commit DB changes!

    :returns: Count of deleted users.
    """
    return User.query.delete()
