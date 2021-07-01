import os
import glob
from functools import wraps

import click
from sqlalchemy.exc import IntegrityError

from src.app import create_app
from src.extensions import db
from src.database import (
    User,
    Chat,
    YandexDiskToken,
    UserSettings,
    UserQuery,
    ChatQuery,
    YandexDiskTokenQuery
)
from src.rq.worker import (
    run_worker as run_rq_worker
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

        user = User.create_fake()
        settings = UserSettings.create_fake(user)

        db.session.add(user)
        db.session.add(settings)

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


@cli.command()
def update_translations() -> None:
    """
    Updates existing translations to match app state.
    """
    translation_directories = os.path.join(
        os.getcwd(),
        "src",
        app.config['BABEL_TRANSLATION_DIRECTORIES']
    )
    translation_directories_exists = os.path.exists(
        translation_directories
    )
    translation_directories_empty = (
        len(os.listdir(translation_directories)) == 0
    ) if translation_directories_exists else True
    translation_directories_valid = (
        translation_directories_exists and
        not translation_directories_empty
    )

    if not translation_directories_valid:
        click.echo(
            "Translations directories not valid. "
            "Initialize at least one language first"
        )

        return

    # https://github.com/python-babel/babel/issues/53
    files_to_translate = " ".join([
        *glob.glob("src/**/*.py", recursive=True),
        *glob.glob("src/**/*.html", recursive=True)
    ])

    temp_file = "messages.pot"
    extract_command = (
        "pybabel extract -F babel.cfg -k lazy_gettext "
        f"-o {temp_file} {files_to_translate}"
    )
    update_command = (
        f"pybabel update -i {temp_file} --no-fuzzy-matching "
        f"-d {translation_directories}"
    )

    if os.system(extract_command):
        return

    if os.system(update_command):
        return

    os.remove(temp_file)

    click.echo("Done")


@cli.command()
def compile_translations() -> None:
    """
    Compiles existing translations.
    """
    translation_directories = os.path.join(
        os.getcwd(),
        "src",
        app.config['BABEL_TRANSLATION_DIRECTORIES']
    )
    translation_directories_exists = os.path.exists(
        translation_directories
    )
    translation_directories_empty = (
        len(os.listdir(translation_directories)) == 0
    ) if translation_directories_exists else True
    translation_directories_valid = (
        translation_directories_exists and
        not translation_directories_empty
    )

    if not translation_directories_valid:
        click.echo(
            "Translations directories not valid. "
            "Initialize at least one language first"
        )

        return

    compile_command = (
        f"pybabel compile -d {translation_directories} --statistics"
    )

    if os.system(compile_command):
        return

    click.echo("Done")


@cli.command()
@click.argument(
    "language_code",
    required=True
)
def init_translations(language_code: str) -> None:
    """
    Initialize new language to use for translations.

    LANGUAGE_CODE is the IETF language tag.
    """
    # https://github.com/python-babel/babel/issues/53
    files_to_translate = " ".join([
        *glob.glob("src/**/*.py", recursive=True),
        *glob.glob("src/**/*.html", recursive=True)
    ])

    temp_file = "messages.pot"
    translation_directories = (
        "src/"
        f"{app.config['BABEL_TRANSLATION_DIRECTORIES']}"
    )
    extract_command = (
        "pybabel extract -F babel.cfg -k lazy_gettext "
        f"-o {temp_file} {files_to_translate}"
    )
    update_command = (
        f"pybabel init -i {temp_file} "
        f"-d {translation_directories} -l {language_code}"
    )

    if os.system(extract_command):
        return

    if os.system(update_command):
        return

    os.remove(temp_file)

    click.echo("Done")


@cli.command()
def run_worker():
    """
    Runs single worker for background tasks.
    """
    run_rq_worker()


if (__name__ == "__main__"):
    cli()
