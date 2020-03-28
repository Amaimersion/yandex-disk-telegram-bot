from enum import IntEnum, unique

from ..db import db


@unique
class ChatType(IntEnum):
    """
    Type of Telegram chat.
    """
    PRIVATE = 1
    GROUP = 2
    SUPERGROUP = 3
    CHANNEL = 4


class Chat(db.Model):
    """
    Telegram chat.
    One user can have multiple chats.
    """
    __tablename__ = "chats"

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
    user = db.relationship(
        'User',
        backref=db.backref(
            'chats',
            lazy="select"
        )
    )

    def __repr__(self):
        return f"<Chat {self.id}>"
