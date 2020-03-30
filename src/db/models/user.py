from enum import IntEnum, unique

from sqlalchemy.sql import func

from ..db import db
from ...localization import SupportedLanguages


@unique
class UserGroup(IntEnum):
    """
    User rights group.
    """
    USER = 1
    TESTER = 2
    ADMIN = 3


class User(db.Model):
    """
    Telegram user.
    """
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    create_date = db.Column(
        db.DateTime(timezone=False),
        server_default=func.now(),
        nullable=False
    )
    last_update_date = db.Column(
        db.DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    telegram_id = db.Column(
        db.Integer,
        unique=True,
        nullable=False,
        comment="Unique ID to identificate user in Telegram"
    )
    is_bot = db.Column(
        db.Boolean,
        nullable=False,
        comment="User is bot in Telegram"
    )
    language = db.Column(
        db.Enum(SupportedLanguages),
        default=SupportedLanguages.EN,
        nullable=False,
        comment="Preferred language of user"
    )
    group = db.Column(
        db.Enum(UserGroup),
        default=UserGroup.USER,
        nullable=False,
        comment="User rights group"
    )
    chats = db.relationship(
        "Chat",
        back_populates="user",
        uselist=True
    )
    yandex_disk_token = db.relationship(
        "YandexDiskToken",
        back_populates="user",
        uselist=False
    )

    def __repr__(self):
        return f"<User {self.id}>"

    @staticmethod
    def create_fake():
        """
        Creates fake user.
        """
        from random import choice

        from faker import Faker

        fake = Faker()

        create_date = fake.date_time_between(
            start_date="-2y",
            end_date="now",
            tzinfo=None
        )
        last_update_date = fake.date_time_between_dates(
            datetime_start=create_date,
            tzinfo=None
        )
        telegram_id = fake.pyint(
            min_value=10000,
            max_value=1000000,
            step=1
        )
        is_bot = (fake.pyint() % 121 == 0)
        language = choice(list(SupportedLanguages))
        group = choice(list(UserGroup))

        return User(
            create_date=create_date,
            last_update_date=last_update_date,
            telegram_id=telegram_id,
            is_bot=is_bot,
            language=language,
            group=group
        )
