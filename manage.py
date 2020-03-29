import click
from sqlalchemy.exc import IntegrityError

from src.app import create_app
from src.db import db, User


app = create_app()
app.config["SQLALCHEMY_ECHO"] = False


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


if (__name__ == "__main__"):
    cli()
