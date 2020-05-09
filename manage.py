from functools import wraps

import click
from sqlalchemy.exc import IntegrityError

from src.app import create_app
from src.database import (
    db,
    User,
    Chat,
    YandexDiskToken,
    UserQuery,
    ChatQuery,
    YandexDiskTokenQuery
)


app = create_app("development")


class PossibleInfiniteLoopError(Exception):
    """
    Indicates that loop probably become an infinite.
    Because of this dangerous loop a script runtime was interrupted.
    """
    pass


class InvalidTableDataError(Exception):
    """
    Indicates that table in DB is invalid
    (data is empty, some required data is NULL, etc.)
    """
    pass


def with_app_context(func):
    """
    Decorator which enables app context.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with app.app_context():
            func(*args, **kwargs)

    return wrapper


@click.group()
def cli():
    """
    Manages the app.
    """
    pass


@cli.command()
@click.option(
    "--count",
    default=5,
    show_default=True,
    help="How many fakes should be added"
)
@with_app_context
def add_fake_users(count: int) -> None:
    """
    Adds fake users in DB.
    """
    i = 0
    error_count = 0

    while (i != count):
        if (error_count >= 5):
            raise PossibleInfiniteLoopError(
                "Too many errors in a row"
            )

        db.session.add(
            User.create_fake()
        )

        try:
            db.session.commit()
            i += 1
            error_count = 0
        except IntegrityError:
            # error because of same `telegram_id`
            error_count += 1

    click.echo(f"Done ({count})")


@cli.command()
@click.option(
    "--count",
    default=8,
    show_default=True,
    help="How many fakes should be added"
)
@with_app_context
def add_fake_chats(count: int) -> None:
    """
    Adds fake chats in DB.
    """
    i = 0
    error_count = 0

    while (i != count):
        if (error_count >= 5):
            raise PossibleInfiniteLoopError(
                "Too many errors in a row"
            )

        chat = Chat.create_fake(None)
        user = UserQuery.get_random_user()

        if (user is None):
            raise InvalidTableDataError(
                "Random user is none. Users table is empty?"
            )

        chat.user = user
        db.session.add(chat)

        try:
            db.session.commit()
            i += 1
            error_count = 0
        except IntegrityError:
            # error because of same `telegram_id`
            error_count += 1

    click.echo(f"Done ({count})")


@cli.command()
@click.option(
    "--count",
    default=3,
    show_default=True,
    help="How many fakes should be added"
)
@with_app_context
def add_fake_yd_tokens(count: int) -> None:
    """
    Adds fake Yandex.Disk tokens in DB.
    """
    free_users_count = UserQuery.get_users_without_yd_token_count()

    if (count > free_users_count):
        raise ValueError(
            f"Number of tokens ({count}) can't be greater than "
            f"number of free users ({free_users_count})"
        )

    i = 0

    while (i != count):
        free_user = UserQuery.get_random_user_without_yd_token()
        result = YandexDiskToken.create_fake(free_user)
        token = result["value"]

        db.session.add(token)
        db.session.commit()

        i += 1

    click.echo(f"Done ({count})")


@cli.command()
@click.option(
    "--users-count",
    default=50,
    show_default=True,
    help="How many user fakes should be added"
)
@click.option(
    "--chats-count",
    default=60,
    show_default=True,
    help="How many chat fakes should be added"
)
@click.option(
    "--yd-tokens-count",
    default=40,
    show_default=True,
    help="How many Y.D. token fakes should be added"
)
@click.pass_context
def add_fake_data(
    context: dict,
    users_count: int,
    chats_count: int,
    yd_tokens_count: int
) -> None:
    """
    Adds fake data in all DB tables.
    """
    context.invoke(add_fake_users, count=users_count)
    context.invoke(add_fake_chats, count=chats_count)
    context.invoke(add_fake_yd_tokens, count=yd_tokens_count)


@cli.command()
@with_app_context
def clear_users() -> None:
    """
    Removes all users from a table.
    """
    count = UserQuery.delete_all_users()
    db.session.commit()

    click.echo(f"Done ({count})")


@cli.command()
@with_app_context
def clear_chats() -> None:
    """
    Removes all chats from a table.
    """
    count = ChatQuery.delete_all_chats()
    db.session.commit()

    click.echo(f"Done ({count})")


@cli.command()
@with_app_context
def clear_yd_tokens() -> None:
    """
    Removes all Yandex.Disk tokens from a table.
    """
    count = YandexDiskTokenQuery.delete_all_yd_tokens()
    db.session.commit()

    click.echo(f"Done ({count})")


@cli.command()
@click.pass_context
def clear_db(context: dict) -> None:
    """
    Removes all data from DB tables.
    """
    context.invoke(clear_users)
    context.invoke(clear_chats)
    context.invoke(clear_yd_tokens)


if (__name__ == "__main__"):
    cli()
