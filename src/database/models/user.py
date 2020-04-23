from enum import IntEnum, unique

from sqlalchemy.sql import func

from src.database import db
from src.localization import SupportedLanguages


@unique
class UserGroup(IntEnum):
    """
    User rights group (access level).

    Access level is presented in ascending order.
    i.e., greater number means higher access (more rights).
    """
    INVALID = 0
    BANNED = 1
    USER = 2
    TESTER = 3
    ADMIN = 4


class User(db.Model):
    """
    Telegram user.
    """
    __tablename__ = "users"

    # Columns
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

    # Relationships
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
        from faker import Faker

        fake = Faker()
        random_number = fake.pyint(
            min_value=1,
            max_value=20,
            step=1
        )
        result = User()

        result.create_date = fake.date_time_between(
            start_date="-2y",
            end_date="now",
            tzinfo=None
        )
        result.last_update_date = fake.date_time_between_dates(
            datetime_start=result.create_date,
            tzinfo=None
        )
        result.telegram_id = fake.pyint(
            min_value=100000,
            max_value=10000000,
            step=1
        )
        result.is_bot = (fake.pyint() % 121 == 0)
        result.language = fake.random_element(list(SupportedLanguages))
        result.group = (
            fake.random_element(list(UserGroup)) if (
                random_number % 20 == 0
            ) else UserGroup.USER
        )

        return result
