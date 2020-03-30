import os
from typing import Union

from sqlalchemy.sql import null
from sqlalchemy.ext.hybrid import hybrid_property
from cryptography.fernet import (
    Fernet,
    InvalidToken as InvalidTokenFernetException
)

from ..db import db


fernet = Fernet(os.getenv("FLASK_SECRET_KEY").encode())


class YandexDiskToken(db.Model):
    """
    Yandex.Disk token.
    One user can have only one token.
    """
    __tablename__ = "yandex_disk_tokens"

    # Columns
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    _access_token = db.Column(
        "access_token",
        db.String,
        nullable=True,
        default=null(),
        comment="Encrypted Y.D. OAuth token"
    )
    access_token_type = db.Column(
        db.String,
        nullable=True,
        default=null(),
        comment="Type of access token"
    )
    access_token_expires_in = db.Column(
        db.Integer,
        nullable=True,
        default=null(),
        comment="Access token lifetime in seconds"
    )
    _refresh_token = db.Column(
        "refresh_token",
        db.String,
        nullable=True,
        default=null(),
        comment="Encrypted Y.D. refresh token to use to update access token"
    )
    _insert_token = db.Column(
        "insert_token",
        db.String,
        nullable=True,
        default=null(),
        comment=(
            "Encrypted token for update controlling. "
            "i.e., you shouldn't insert values if you don't know insert token"
        )
    )
    insert_token_expires_in = db.Column(
        db.Integer,
        nullable=True,
        default=null(),
        comment="Insert token lifetime in seconds"
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False,
        comment="Token belongs to this user"
    )

    # Relationships
    user = db.relationship(
        'User',
        backref=db.backref(
            'token',
            lazy="select",
            uselist=False
        )
    )

    def __init__(self, **kwargs):
        super(YandexDiskToken, self).__init__(**kwargs)

        if ("_access_token" in kwargs):
            raise AttributeError("`access_token` can't be accessed directly")
        elif ("_refresh_token" in kwargs):
            raise AttributeError("`refresh_token` can't be accessed directly")
        elif ("_insert_token" in kwargs):
            raise AttributeError("`insert_token` can't be accessed directly")

    def __repr__(self):
        return f"<YD Token {self.id}>"

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    @hybrid_property
    def access_token(self):
        raise AttributeError("`access_token` can't be accessed directly")

    @access_token.setter
    def access_token(self, new_value):
        raise AttributeError("`access_token` can't be accessed directly")

    @hybrid_property
    def refresh_token(self):
        raise AttributeError("`refresh_token` can't be accessed directly")

    @refresh_token.setter
    def refresh_token(self, new_value):
        raise AttributeError("`refresh_token` can't be accessed directly")

    @hybrid_property
    def insert_token(self):
        raise AttributeError("`insert_token` can't be accessed directly")

    @insert_token.setter
    def insert_token(self, new_value):
        raise AttributeError("`insert_token` can't be accessed directly")

    def _set_token(self, **kwargs) -> None:
        """
        Sets encrypted token.

        :param token_attribute_name: Attribute name of token in instance.
        :param data: Data to set.
        """
        data = kwargs["data"]
        token_attribute_name = kwargs["token_attribute_name"]

        if (data is None):
            self[token_attribute_name] = None
        else:
            encrypted_data = fernet.encrypt(data.encode())
            self[token_attribute_name] = encrypted_data.decode()

    def _get_token(self, **kwargs) -> Union[str, None]:
        """
        Returns decrypted token.

        :param token_attribute_name:
        Attribute name of token in instance.
        :param expires_attribute_name:
        Optional.
        Token lifetime in seconds.
        If specified, expiration date will be checked.

        :returns: Decrypted token or `None` if data is empty.

        :raises DataCorruptedException: Data from DB is corrupted.
        :raises InvalidTokenException: Encrypted token is invalid.
        """
        token_attribute_name = kwargs["token_attribute_name"]
        encrypted_token = self[token_attribute_name]

        if (encrypted_token is None):
            return None

        expires_attribute_name = kwargs.get("expires_attribute_name")
        token_lifetime = None

        if (expires_attribute_name is not None):
            token_lifetime = self[expires_attribute_name]

            if (not isinstance(token_lifetime, int)):
                raise DataCorruptedException("Token lifetime is not integer")

        encrypted_token = encrypted_token.encode()
        decrypted_token = None

        try:
            decrypted_token = fernet.decrypt(encrypted_token, token_lifetime)
        except InvalidTokenFernetException:
            raise InvalidTokenException("Token is invalid")

        decrypted_token = decrypted_token.decode()

        return decrypted_token

    def set_access_token(self, token: Union[str, None]) -> None:
        """
        Sets encrypted access token.
        """
        self._set_token(
            token_attribute_name="_access_token",
            data=token
        )

    def get_access_token(self) -> Union[str, None]:
        """
        Returns decrypted access token.

        :raises DataCorruptedException: Data from DB is corrupted.
        :raises InvalidTokenException: Encrypted token is invalid.
        """
        return self._get_token(
            token_attribute_name="_access_token",
            expires_attribute_name="access_token_expires_in"
        )

    def set_refresh_token(self, token: Union[str, None]) -> None:
        """
        Sets encrypted refresh token.
        """
        self._set_token(
            token_attribute_name="_refresh_token",
            data=token
        )

    def get_refresh_token(self) -> Union[str, None]:
        """
        Returns decrypted refresh token.

        :raises DataCorruptedException: Data from DB is corrupted.
        :raises InvalidTokenException: Encrypted token is invalid.
        """
        return self._get_token(
            token_attribute_name="_refresh_token"
        )

    def set_insert_token(self, token: Union[str, None]) -> None:
        """
        Sets encrypted insert token.
        """
        self._set_token(
            token_attribute_name="_insert_token",
            data=token
        )

    def get_insert_token(self) -> Union[str, None]:
        """
        Returns decrypted insert token.

        :raises DataCorruptedException: Data from DB is corrupted.
        :raises InvalidTokenException: Encrypted token is invalid.
        """
        return self._get_token(
            token_attribute_name="_insert_token",
            expires_attribute_name="insert_token_expires_in"
        )


class DataCorruptedException(Exception):
    """
    Data in databse is corrupted.
    For example, if some required fields is missing or
    have invalid type.
    """
    pass


class InvalidTokenException(Exception):
    """
    Token is invalid. From `cryptography` documentation:
    "A token may be invalid for a number of reasons:
    it is older than the token lifetime, it is malformed,
    or it does not have a valid signature."
    """
    pass
