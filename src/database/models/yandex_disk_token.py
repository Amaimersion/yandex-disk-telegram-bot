from typing import Union

from flask import current_app
from sqlalchemy.sql import null
from sqlalchemy.ext.hybrid import hybrid_property
from cryptography.fernet import (
    Fernet,
    InvalidToken as InvalidTokenFernetError
)

from src.database import db


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
        db.BigInteger,
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
            "Encrypted token for DB update controlling. "
            "i.e., you shouldn't insert values if you don't know insert token"
        )
    )
    insert_token_expires_in = db.Column(
        db.BigInteger,
        nullable=True,
        default=null(),
        comment="Insert token lifetime in seconds"
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False,
        comment="Tokens belongs to this user"
    )

    # Relationships
    user = db.relationship(
        'User',
        back_populates="yandex_disk_token",
        uselist=False
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

    @staticmethod
    def create_fake(user) -> dict:
        """
        Creates fake Yandex.Disk token.

        There is two types of token: "pending" or "received".

        Pending means the app wants to write in `access_token`
        column, but request to Yandex not maded at the moment.
        If app received invalid `insert_token` from user, then
        it shouldn't make request to Yandex.

        Received means the app successfully made a request to Yandex
        and `insert_token` not exists in a row, because `INSERT`
        operation was successfully completed.

        :param user: User to associate token with.

        :returns: "Pending" token (chance is 1/10) or
        "received" token (chance is 9/10).
        """
        from faker import Faker

        fake = Faker()
        result = YandexDiskToken(user=user)
        result_type = None
        random_number = fake.pyint(
            min_value=1,
            max_value=10,
            step=1
        )

        if (random_number % 10):
            result_type = "pending"

            result.set_access_token(
                fake.pystr(
                    min_chars=32,
                    max_chars=32
                )
            )
            result.set_refresh_token(
                fake.pystr(
                    min_chars=32,
                    max_chars=32
                )
            )

            result.access_token_type = "bearer"
            result.access_token_expires_in = fake.pyint(
                min_value=31536000,
                max_value=63072000,
                step=1
            )
        else:
            result_type = "received"

            result.set_insert_token(
                fake.pystr(
                    min_chars=32,
                    max_chars=32
                )
            )

            result.insert_token_expires_in = fake.pyint(
                min_value=600,
                max_value=900,
                step=100
            )

        return {
            "value": result,
            "type": result_type
        }

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

    def set_access_token(self, token: Union[str, None]) -> None:
        """
        Sets encrypted access token.
        """
        self._set_token(
            token_attribute_name="_access_token",
            value=token
        )

    def get_access_token(self) -> Union[str, None]:
        """
        Returns decrypted access token.

        :raises DataCorruptedError:
        Data in DB is corrupted.
        :raises InvalidTokenError:
        Encrypted token is invalid or expired.
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
            value=token
        )

    def get_refresh_token(self) -> Union[str, None]:
        """
        Returns decrypted refresh token.

        :raises DataCorruptedError:
        Data in DB is corrupted.
        :raises InvalidTokenError:
        Encrypted token is invalid.
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
            value=token
        )

    def get_insert_token(self) -> Union[str, None]:
        """
        Returns decrypted insert token.

        :raises DataCorruptedError:
        Data in DB is corrupted.
        :raises InvalidTokenError:
        Encrypted token is invalid or expired.
        """
        return self._get_token(
            token_attribute_name="_insert_token",
            expires_attribute_name="insert_token_expires_in"
        )

    def have_access_token(self) -> bool:
        """
        :returns: `True` if `access_token` contains
        any value otherwise `False`.
        """
        return self._have_token(
            token_attribute_name="_access_token"
        )

    def have_refresh_token(self) -> bool:
        """
        :returns: `True` if `refresh_token` contains
        any value otherwise `False`.
        """
        return self._have_token(
            token_attribute_name="_refresh_token"
        )

    def have_insert_token(self) -> bool:
        """
        :returns: `True` if `insert_token` contains
        any value otherwise `False`.
        """
        return self._have_token(
            token_attribute_name="_insert_token"
        )

    def clear_access_token(self) -> None:
        """
        Clears all data that belongs to access token.

        - perform a commit in order to save changes!
        """
        self.access_token_type = null()

        return self._clear_token(
            token_attribute_name="_access_token",
            expires_attribute_name="access_token_expires_in"
        )

    def clear_refresh_token(self) -> None:
        """
        Clears all data that belongs to refresh token.

        - perform a commit in order to save changes!
        """
        return self._clear_token(
            token_attribute_name="_refresh_token"
        )

    def clear_insert_token(self) -> None:
        """
        Clears all data that belongs to insert token.

        - perform a commit in order to save changes!
        """
        return self._clear_token(
            token_attribute_name="_insert_token",
            expires_attribute_name="insert_token_expires_in"
        )

    def clear_all_tokens(self) -> None:
        """
        Clears all data that belongs to any kind of token.

        - perform a commit in order to save changes!
        """
        self.clear_access_token()
        self.clear_refresh_token()
        self.clear_insert_token()

    def _set_token(self, **kwargs) -> None:
        """
        Sets encrypted token.

        :param token_attribute_name:
        Name of token attribute in class.
        :param value: Value to set.
        """
        fernet = Fernet(current_app.secret_key.encode())
        token_attribute_name = kwargs["token_attribute_name"]
        value = kwargs["value"]

        if (value is None):
            self[token_attribute_name] = None
        else:
            encrypted_data = fernet.encrypt(value.encode())
            self[token_attribute_name] = encrypted_data.decode()

    def _get_token(self, **kwargs) -> Union[str, None]:
        """
        Returns decrypted token.

        :param token_attribute_name:
        Name of token attribute in class.
        :param expires_attribute_name:
        Optional. Token lifetime in seconds.
        If specified, expiration date will be checked.

        :returns: Decrypted token or `None` if value is NULL.

        :raises DataCorruptedError: Data in DB is corrupted.
        :raises InvalidTokenError: Encrypted token is invalid.
        """
        fernet = Fernet(current_app.secret_key.encode())
        token_attribute_name = kwargs["token_attribute_name"]
        encrypted_token = self[token_attribute_name]

        if (encrypted_token is None):
            return None

        token_lifetime = None
        expires_attribute_name = kwargs.get("expires_attribute_name")

        if (expires_attribute_name is not None):
            token_lifetime = self[expires_attribute_name]

            if (not isinstance(token_lifetime, int)):
                raise DataCorruptedError("Token lifetime is not an integer")

        encrypted_token = encrypted_token.encode()
        decrypted_token = None

        try:
            decrypted_token = fernet.decrypt(encrypted_token, token_lifetime)
        except InvalidTokenFernetError:
            raise InvalidTokenError("Token is invalid or expired")

        decrypted_token = decrypted_token.decode()

        return decrypted_token

    def _have_token(self, **kwargs) -> bool:
        """
        :param token_attribute_name:
        Name of token attribute in class.

        :returns:
        `True` if token contains any value, `False` otherwise.
        """
        token_attribute_name = kwargs["token_attribute_name"]
        value = self[token_attribute_name]

        return (
            isinstance(value, str) and
            len(value) > 0
        )

    def _clear_token(self, **kwargs) -> None:
        """
        Clears token data.

        - perform a commit in order to save changes!

        :param token_attribute_name:
        Name of token attribute in class.
        :param expires_attribute_name:
        Optional. Token lifetime in seconds.
        If specified, expiration date will be cleared.
        """
        token_attribute_name = kwargs["token_attribute_name"]
        expires_attribute_name = kwargs.get("expires_attribute_name")

        self[token_attribute_name] = null()

        if (expires_attribute_name):
            self[expires_attribute_name] = null()


class DataCorruptedError(Exception):
    """
    Data in databse is corrupted.
    For example, when some of required fields
    is missing or have invalid type.
    """
    pass


class InvalidTokenError(Exception):
    """
    Token is invalid. From `cryptography` documentation:
    "A token may be invalid for a number of reasons:
    it is older than the token lifetime, it is malformed,
    or it does not have a valid signature."
    """
    pass
