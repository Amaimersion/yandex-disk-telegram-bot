from sqlalchemy.sql import null

from ..db import db


class YandexDiskToken(db.Model):
    """
    Yandex.Disk token.
    One user can have only one token.
    """
    __tablename__ = "yandex_disk_tokens"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    access_token = db.Column(
        db.String,
        nullable=True,
        default=null(),
        comment="Yandex.Disk OAuth token"
    )
    refresh_token = db.Column(
        db.String,
        nullable=True,
        default=null(),
        comment="Refresh token to use to update access token"
    )
    access_token_type = db.Column(
        db.String,
        nullable=True,
        default=null(),
        comment="Type of access token"
    )
    access_token_expires_in = db.Column(
        db.DateTime(timezone=False),
        nullable=True,
        default=null(),
        comment="Access token expires on this date (UTC+0)"
    )
    insert_token = db.Column(
        db.String,
        nullable=True,
        default=null(),
        comment=(
            "Token for update controlling. "
            "i.e., you shouldn't insert values if you don't know insert token"
        )
    )
    insert_token_expires_in = db.Column(
        db.DateTime(timezone=False),
        nullable=True,
        default=null(),
        comment="Insert token expires on this date (UTC+0)"
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False,
        comment="Token belongs to this user"
    )
    user = db.relationship(
        'User',
        backref=db.backref(
            'token',
            lazy="select",
            uselist=False
        )
    )

    def __repr__(self):
        return f"<YD Token {self.id}>"
