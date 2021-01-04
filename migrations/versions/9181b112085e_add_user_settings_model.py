"""Add user settings model

Revision ID: 9181b112085e
Revises: c8db92e01cf4
Create Date: 2021-01-04 11:21:12.968252

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base


# revision identifiers, used by Alembic.
revision = '9181b112085e'
down_revision = 'c8db92e01cf4'
branch_labels = None
depends_on = None


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = sa.Column(
        sa.Integer,
        primary_key=True
    )
    settings = orm.relationship(
        "UserSettings",
        back_populates="user",
        uselist=False
    )


class UserSettings(Base):
    __tablename__ = "user_settings"
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.id"),
        primary_key=True,
        nullable=False,
        comment="Data related to this user"
    )
    last_update_date = sa.Column(
        sa.DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    default_upload_folder = sa.Column(
        sa.String,
        nullable=True,
        default="Telegram Bot",
        comment="By default, files will be uploaded in this folder"
    )
    user = orm.relationship(
        "User",
        back_populates="settings",
        uselist=False
    )


def upgrade():
    """
    It is manual upgrade which based on
    https://stackoverflow.com/a/24623979/8445442
    """
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    UserSettings.__table__.create(bind)

    user_settings = {
        str(user.id): UserSettings(user=user)
        for user in session.query(User).all()
    }
    session.add_all(user_settings.values())

    for user in session.query(User).all():
        user.settings = user_settings[str(user.id)]

    session.commit()


def downgrade():
    """
    It is manual downgrade which based on
    https://stackoverflow.com/a/24623979/8445442
    """
    op.drop_table(UserSettings.__tablename__)
