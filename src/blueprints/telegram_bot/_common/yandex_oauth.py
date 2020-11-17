import base64
import secrets
from enum import Enum, auto
from typing import Union

from flask import current_app
import jwt

from src.api import yandex
from src.extensions import db
from src.database import (
    User,
    YandexDiskToken,
    UserQuery,
    ChatQuery
)


class InvalidState(Exception):
    """
    Provided state is invalid
    (invalid Base64, missing data, wrong data, etc.).
    For security reasons there is no exact reason.
    """
    pass


class ExpiredInsertToken(Exception):
    """
    Provided insert token is expired.
    """
    pass


class InvalidInsertToken(Exception):
    """
    Provided insert token (extracted from state) is invalid.
    Most probably new state was requested and old one
    was passed for handling.
    """


class YandexRequestError(Exception):
    """
    Unexpected error occurred during Yandex.OAuth HTTP request.
    """
    pass


class MissingData(Exception):
    """
    Requested data is missing.
    """
    pass


class YandexOAuthClient:
    """
    Base class for all Yandex.OAuth clients.
    """
    def encode_state(self, user_id: int, insert_token: str) -> str:
        """
        :returns:
        JWT which should be used as a value for `state`
        Yandex.OAuth key. It is urlsafe base64 string.
        """
        return base64.urlsafe_b64encode(
            jwt.encode(
                {
                    "user_id": user_id,
                    "insert_token": insert_token
                },
                current_app.secret_key.encode(),
                algorithm="HS256"
            )
        ).decode()

    def decode_state(self, state: str) -> dict:
        """
        :param state:
        A state from `create_state()`.

        :returns:
        A dict of arguments that were passed into `create_state()`.

        :raises:
        `InvalidState`.
        """
        encoded_state = None

        try:
            encoded_state = base64.urlsafe_b64decode(
                state.encode()
            ).decode()
        except Exception:
            raise InvalidState()

        decoded_state = None

        try:
            decoded_state = jwt.decode(
                encoded_state,
                current_app.secret_key.encode(),
                algorithm="HS256"
            )
        except Exception:
            raise InvalidState()

        user_id = decoded_state.get("user_id")
        insert_token = decoded_state.get("insert_token")

        if not any((user_id, insert_token)):
            raise InvalidState()

        return {
            "user_id": user_id,
            "insert_token": insert_token
        }

    def get_user(self, user_id: int, insert_token: str) -> User:
        """
        :param user_id:
        DB id of needed user.
        :param insert_token:
        User will be returned only in case when provided
        insert token matchs with one from DB. This means
        you are allowed to modify this DB user.
        Insert token of that user can be modified in futher by
        some another operation, so, you should call this function
        once and reuse returned result.

        :returns:
        DB user.

        :raises:
        `MissingData`, `ExpiredInsertToken`, `InvalidInsertToken`.
        """
        user = UserQuery.get_user_by_id(user_id)

        if (
            user is None or
            # for some reason `yandex_disk_token` not created,
            # it is not intended behavior.
            user.yandex_disk_token is None
        ):
            raise MissingData()

        db_insert_token = None

        try:
            db_insert_token = user.yandex_disk_token.get_insert_token()
        except Exception:
            raise ExpiredInsertToken()

        if (insert_token != db_insert_token):
            raise InvalidInsertToken()

        return user

    def request_access_token(self, code="", refresh_token="") -> dict:
        """
        Makes HTTP request to Yandex.OAuth API to get access token.

        - you should specify only one parameter:
        `code` or `refresh_token`. If specified both, then `code`
        will be selected. If nothing is specified, then an error
        will be thrown.

        :returns:
        `ok` indicates status of operation.
        If `ok = False`, then `error` will contain
        `title` and optional `description`.
        if `ok = True`, then `access_token`, `token_type`,
        `expires_in`, `refresh_token` will be provided.

        :raises:
        `YandexRequestError`.
        """
        response = None
        kwargs = {}

        if code:
            kwargs["grant_type"] = "authorization_code"
            kwargs["code"] = code
        elif refresh_token:
            kwargs["grant_type"] = "refresh_token"
            kwargs["refresh_token"] = refresh_token
        else:
            raise Exception("Invalid arguments")

        try:
            response = yandex.get_access_token(
                **kwargs
            )["content"]
        except Exception as error:
            raise YandexRequestError(str(error))

        if "error" in response:
            return {
                "ok": False,
                "error": {
                    "title": response["error"],
                    "description": response.get("error_description")
                }
            }

        return {
            "ok": True,
            "access_token": response["access_token"],
            "token_type": response["token_type"],
            "expires_in": response["expires_in"],
            "refresh_token": response["refresh_token"],
        }

    def set_access_token(self, user: User, code: str) -> dict:
        """
        Makes request to Yandex.OAuth server, gets access
        token and saves it.

        - on success clears insert token.
        - perform a DB commit in order to save changes!

        :param user:
        DB user.
        :param code:
        Code from Yandex which was given to user.

        :returns:
        `ok` which contains status of operation.
        `error` from Yandex in case of `ok = False`,
        `error` contains `title` and optional `description`.

        :raises:
        `YandexRequestError`.
        """
        response = self.request_access_token(code=code)

        if not response["ok"]:
            return response

        user.yandex_disk_token.clear_insert_token()
        user.yandex_disk_token.set_access_token(
            response["access_token"]
        )
        user.yandex_disk_token.access_token_type = (
            response["token_type"]
        )
        user.yandex_disk_token.access_token_expires_in = (
            response["expires_in"]
        )
        user.yandex_disk_token.set_refresh_token(
            response["refresh_token"]
        )

        return {
            "ok": True
        }

    def refresh_access_token(self, user: User) -> dict:
        """
        Similar to `set_access_token()`, but uses user
        refresh token from DB.

        - perform DB commit in order to save changes!
        - `error` not always presented in case of `ok = False`.

        :raises:
        `YandexRequestError`.
        """
        refresh_token = user.yandex_disk_token.get_refresh_token()

        if refresh_token is None:
            return {
                "ok": False
            }

        response = self.request_access_token(refresh_token=refresh_token)

        if not response["ok"]:
            return response

        user.yandex_disk_token.clear_insert_token()
        user.yandex_disk_token.set_access_token(
            response["access_token"]
        )
        user.yandex_disk_token.access_token_type = (
            response["token_type"]
        )
        user.yandex_disk_token.access_token_expires_in = (
            response["expires_in"]
        )
        user.yandex_disk_token.set_refresh_token(
            response["refresh_token"]
        )

        return {
            "ok": True
        }

    def have_valid_access_token(self, user: User) -> bool:
        """
        :returns:
        User have valid (not expired) access token.
        """
        token = user.yandex_disk_token

        if not token:
            return False

        if not token.have_access_token():
            return False

        try:
            # there will be errors in case of
            # expired or invalid token
            token.get_access_token()
        except Exception:
            return False

        return True

    def create_insert_token(self, user: User) -> str:
        """
        Creates insert token (used to insert new data).

        WARNING: it clears all previous data
        (access token, refresh token, etc)!

        - perform DB commit in order to save changes!

        :returns:
        Created insert token.

        :raises:
        `MissingData` (DB data is corrupted or problems with DB).
        """
        user.yandex_disk_token.clear_all_tokens()
        user.yandex_disk_token.set_insert_token(
            secrets.token_hex(
                current_app.config[
                    "YANDEX_OAUTH_API_INSERT_TOKEN_BYTES"
                ]
            )
        )
        user.yandex_disk_token.insert_token_expires_in = (
            current_app.config[
                "YANDEX_OAUTH_API_INSERT_TOKEN_LIFETIME"
            ]
        )

        # it is necessary to check if we able to get
        # valid token after inseting
        insert_token = user.yandex_disk_token.get_insert_token()

        if insert_token is None:
            raise MissingData("Insert token is NULL")

        return insert_token


class YandexOAuthAutoCodeClient(YandexOAuthClient):
    """
    Implements https://yandex.ru/dev/oauth/doc/dg/reference/auto-code-client.html # noqa
    """
    def before_user_interaction(self, user: User) -> dict:
        """
        This function should be executed before user interation.

        :returns:
        `status` that contains operation status. See `OperationStatus`
        documentation for more. In case of `status = CONTINUE_TO_URL`
        there will be both `url` and `lifetime`. User should open this
        url, after `lifetime` seconds this url will be expired.
        In case of any other `status` further user actions not needed
        because this user already have valid access token.

        :raises:
        `YandexRequestError`, `MissingData`.
        """
        # it can be not created if it is a new user
        if not user.yandex_disk_token:
            db.session.add(
                YandexDiskToken(user=user)
            )
        elif self.have_valid_access_token(user):
            return {
                "status": OperationStatus.HAVE_ACCESS_TOKEN
            }

        refresh_result = self.refresh_access_token(user)

        # if `ok = False`, then there can be useful error message
        # from Yandex with some description. At the moment
        # we will do nothing with it and just continue
        # with need of user interaction
        if refresh_result["ok"]:
            db.session.commit()

            return {
                "status": OperationStatus.ACCESS_TOKEN_REFRESHED
            }

        insert_token = self.create_insert_token(user)
        state = self.encode_state(user.id, insert_token)
        url = yandex.create_user_oauth_url(state)
        lifetime_in_seconds = (
            user.yandex_disk_token.insert_token_expires_in
        )

        db.session.commit()

        return {
            "status": OperationStatus.CONTINUE_TO_URL,
            "url": url,
            "lifetime": lifetime_in_seconds
        }

    def after_success_redirect(self, state: str, code: str) -> dict:
        """
        Should be called after Yandex successful redirect
        (when there is both `code` and `state` parameters).
        Performs needed operations to end user authorization.

        :returns:
        `ok` which contains status of setting of access token.
        `error` from Yandex in case of `ok = False`,
        `error` contains `title` and optional `description`.
        If `ok = False`, you should notify user about occured error
        and user should request new authorization link because old
        one will become invalid.
        `user` is DB user.

        :raises:
        - `InvalidState`, `ExpiredInsertToken`, `MissingData`,
        `InvalidInsertToken`, `YandexRequestError`.
        - Other errors (`Exception`) should be considered as
        internal server error.
        """
        data = self.decode_state(state)
        user = self.get_user(
            data["user_id"],
            data["insert_token"]
        )
        result = self.set_access_token(user, code)
        result["user"] = user

        if not result["ok"]:
            user.yandex_disk_token.clear_insert_token()

        db.session.commit()

        return result

    def after_error_redirect(self, state: str) -> None:
        """
        Should be called after Yandex error redirect
        (when there is both `error` and `state` parameters).

        - if function successfully ends, then old user authorization
        link will become invalid.

        :raises:
        `InvalidState`, `ExpiredInsertToken`,
        `InvalidInsertToken`, `MissingData`.
        """
        data = self.decode_state(state)
        user = self.get_user(
            data["user_id"],
            data["insert_token"]
        )

        user.yandex_disk_token.clear_insert_token()
        db.session.commit()


class YandexOAuthConsoleClient(YandexOAuthClient):
    pass


class OperationStatus(Enum):
    """
    Status of requested operation.
    """
    # User already have valid access token.
    # No further actions is required
    HAVE_ACCESS_TOKEN = auto()

    # Access token was successfully refreshed.
    # No further actions is required
    ACCESS_TOKEN_REFRESHED = auto()

    # User should manually open an URL
    CONTINUE_TO_URL = auto()
