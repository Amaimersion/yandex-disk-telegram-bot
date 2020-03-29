import click
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import func

from src.app import create_app
from src.db import db, User, Chat


app = create_app()


@click.group()
def cli():
    """
    Manages the app.
    """
    pass


@cli.command()
@click.option(
    "--count",
    default=1,
    show_default=True,
    help="How many fake users should be added"
)
def add_fake_users(count):
    """
    Add fake users in DB.
    """
    i = 0

    while (i != count):
        user = User.create_fake()

        with app.app_context():
            db.session.add(user)

            try:
                db.session.commit()
                i += 1
            except IntegrityError:
                # same telegram_id
                pass

    click.echo("Added")


@cli.command()
@click.option(
    "--count",
    default=1,
    show_default=True,
    help="How many fake chats should be added"
)
def add_fake_chats(count):
    """
    Add fake chats in DB.
    """
    i = 0

    while (i != count):
        chat = Chat.create_fake()

        with app.app_context():
            random_user = User.query.order_by(func.random()).first()

            if (random_user is None):
                raise Exception("Random user is none. Users table is empty?")

            chat.user = random_user

            db.session.add(chat)

            try:
                db.session.commit()
                i += 1
            except IntegrityError:
                # same telegram_id
                pass

    click.echo("Added")


if (__name__ == "__main__"):
    cli()
