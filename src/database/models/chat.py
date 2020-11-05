from enum import IntEnum, unique

from src.extensions import db


@unique
class ChatType(IntEnum):
    """
    Type of Telegram chat.
    """
    UNKNOWN = 0
    PRIVATE = 1
    GROUP = 2
    SUPERGROUP = 3
    CHANNEL = 4

    @staticmethod
    def get(type_name: str) -> int:
        """
        Return type by Telegram name.
        """
        type_name = type_name.lower()
        types = {
            "private": ChatType.PRIVATE,
            "group": ChatType.GROUP,
            "supergroup": ChatType.SUPERGROUP,
            "channel": ChatType.CHANNEL
        }

        return types.get(type_name, ChatType.UNKNOWN)


class Chat(db.Model):
    """
    Telegram chat.
    One user can have multiple chats.
    """
    __tablename__ = "chats"

    # Columns
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    telegram_id = db.Column(
        db.BigInteger,
        unique=True,
        nullable=False,
        comment="Unique ID to identificate chat in Telegram"
    )
    type = db.Column(
        db.Enum(ChatType),
        nullable=False,
        comment="Type of Telegram chat"
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        comment="Through this chat message can be sent to this user"
    )

    # Relationships
    user = db.relationship(
        "User",
        back_populates="chats",
        uselist=False
    )

    def __repr__(self):
        return f"<Chat {self.id}>"

    @staticmethod
    def create_fake(user):
        """
        Creates fake chat.

        :param user: User to associate created chat with.
        """
        from faker import Faker

        fake = Faker()
        random_number = fake.pyint(
            min_value=1,
            max_value=10,
            step=1
        )
        result = Chat(user=user)

        result.telegram_id = fake.pyint(
            min_value=10000000,
            max_value=10000000000,
            step=1
        )
        result.type = (
            fake.random_element(list(ChatType)) if (
                random_number % 10 == 0
            ) else ChatType.PRIVATE
        )

        return result
