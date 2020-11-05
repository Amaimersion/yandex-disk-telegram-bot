import base64

from flask import (
    request,
    abort,
    render_template,
    current_app
)
import jwt

from src.extensions import db
from src.database import (
    UserQuery,
    ChatQuery
)
from src.api import yandex, telegram
from src.blueprints.telegram_bot import telegram_bot_blueprint as bp
from src.blueprints.utils import (
    get_current_datetime
)
from src.blueprints.telegram_bot.webhook.commands import CommandName
from .exceptions import (
    InvalidCredentials,
    LinkExpired,
    InvalidInsertToken
)


@bp.route("/yandex_disk_authorization")
def yd_auth():
    """
    Handles user redirect from Yandex OAuth page.
    """
    if (is_error_request()):
        return handle_error()
    elif (is_success_request()):
        return handle_success()
    else:
        abort(400)


def is_error_request() -> bool:
    """
    :returns: Incoming request is a failed user authorization.
    """
    state = request.args.get("state", "")
    error = request.args.get("error", "")

    return (
        len(state) > 0 and
        len(error) > 0
    )


def is_success_request() -> bool:
    """
    :returns: Incoming request is a successful user authorization.
    """
    state = request.args.get("state", "")
    code = request.args.get("code", "")

    return (
        len(state) > 0 and
        len(code) > 0
    )


def handle_error():
    """
    Handles failed user authorization.
    """
    try:
        db_user = get_db_user()
        db_user.yandex_disk_token.clear_insert_token()
        db.session.commit()
    except Exception:
        pass

    return create_error_response()


def handle_success():
    """
    Handles success user authorization.
    """
    db_user = None

    try:
        db_user = get_db_user()
    except InvalidCredentials:
        return create_error_response("invalid_credentials")
    except LinkExpired:
        return create_error_response("link_expired")
    except InvalidInsertToken:
        return create_error_response("invalid_insert_token")
    except Exception as error:
        print(error)
        return create_error_response("internal_server_error")

    code = request.args["code"]
    yandex_response = None

    try:
        yandex_response = yandex.get_access_token(
            grant_type="authorization_code",
            code=code
        )["content"]
    except Exception as error:
        print(error)
        return create_error_response("internal_server_error")

    if ("error" in yandex_response):
        db_user.yandex_disk_token.clear_all_tokens()
        db.session.commit()

        return create_error_response(
            error_code="internal_server_error",
            raw_error_title=yandex_response["error"],
            raw_error_description=yandex_response.get("error_description")
        )

    db_user.yandex_disk_token.clear_insert_token()
    db_user.yandex_disk_token.set_access_token(
        yandex_response["access_token"]
    )
    db_user.yandex_disk_token.access_token_type = (
        yandex_response["token_type"]
    )
    db_user.yandex_disk_token.access_token_expires_in = (
        yandex_response["expires_in"]
    )
    db_user.yandex_disk_token.set_refresh_token(
        yandex_response["refresh_token"]
    )
    db.session.commit()

    private_chat = ChatQuery.get_private_chat(db_user.id)

    if (private_chat):
        current_datetime = get_current_datetime()
        date = current_datetime["date"]
        time = current_datetime["time"]
        timezone = current_datetime["timezone"]

        telegram.send_message(
            chat_id=private_chat.telegram_id,
            parse_mode="HTML",
            text=(
                "<b>Access to Yandex.Disk Granted</b>"
                "\n\n"
                "My access was attached to your Telegram account "
                f"on {date} at {time} {timezone}."
                "\n\n"
                "If it wasn't you, then detach this access with "
                f"{CommandName.YD_REVOKE.value}"
            )
        )

    return create_success_response()


def create_error_response(
    error_code: str = None,
    raw_error_title: str = None,
    raw_error_description: str = None
):
    """
    :param error_code: Name of error for user friendly
    information. If not specified, then defaults to
    `error` argument from request.
    :param raw_error_title: Raw error title for
    debugging purposes. If not specified, then defaults to
    `error_code` argument.
    :param raw_error_description: Raw error description
    for debugging purposes. If not specified, then defaults to
    `error_description` argument from request.

    :returns: Rendered template for error page.
    """
    possible_errors = {
        "access_denied": {
            "title": "Access Denied",
            "description": (
                "You refused to grant me "
                "access to your Yandex.Disk."
            )
        },
        "unauthorized_client": {
            "title": "Application is unavailable",
            "description": (
                "There is a problems with the me. "
                "Try later please."
            )
        },
        "invalid_credentials": {
            "title": "Invalid credentials",
            "description": "Your credentials is not valid."
        },
        "invalid_insert_token": {
            "title": "Invalid credentials",
            "description": (
                "Your credentials is not valid anymore. "
                "Request a new authorization link."
            )
        },
        "link_expired": {
            "title": "Authorization link has expired",
            "description": (
                "Your authorization link has expired. "
                "Request a new one."
            )
        },
        "internal_server_error": {
            "title": "Internal server error",
            "description": (
                "At the moment i can't handle you "
                "because of my internal error. "
                "Try later please."
            )
        }
    }
    state = request.args.get("state")
    error = request.args.get("error")
    error_description = request.args.get("error_description")

    if (error_code is None):
        error_code = error

    error_info = possible_errors.get(error_code, {})

    return render_template(
        "telegram_bot/yd_auth/error.html",
        error_code=error_code,
        error_title=error_info.get("title"),
        error_description=error_info.get("description"),
        raw_error_title=(raw_error_title or error_code),
        raw_error_description=(raw_error_description or error_description),
        raw_state=state
    )


def create_success_response():
    """
    :returns: Rendered template for success page.
    """
    return render_template(
        "telegram_bot/yd_auth/success.html"
    )


def get_db_user():
    """
    - `insert_token` will be checked. If it is not valid,
    an error will be thrown. You shouldn't clear any tokens
    in case of error, because provided tokens is not known
    to attacker (potential).
    - you shouldn't try to avoid checking logic! It is really
    unsafe to access DB user without `insert_token`.

    :returns: User from DB based on incoming `state` from request.
    This user have `yandex_disk_token` property which is
    not `None`.

    :raises InvalidCredentials: If `state` have invalid
    data or user not found in DB.
    :raises LinkExpired: Requested link is expired and
    not valid anymore.
    :raises InvalidInsertToken: Provided `insert_token`
    is not valid.
    """
    base64_state = request.args["state"]
    encoded_state = None
    decoded_state = None

    try:
        encoded_state = base64.urlsafe_b64decode(
            base64_state.encode()
        ).decode()
    except Exception:
        raise InvalidCredentials()

    try:
        decoded_state = jwt.decode(
            encoded_state,
            current_app.secret_key.encode(),
            algorithm="HS256"
        )
    except Exception:
        raise InvalidCredentials()

    incoming_user_id = decoded_state.get("user_id")
    incoming_insert_token = decoded_state.get("insert_token")

    if (
        incoming_user_id is None or
        incoming_insert_token is None
    ):
        raise InvalidCredentials()

    db_user = UserQuery.get_user_by_id(int(incoming_user_id))

    if (
        db_user is None or
        # for some reason `yandex_disk_token` not created,
        # it is not intended behavior.
        db_user.yandex_disk_token is None
    ):
        raise InvalidCredentials()

    db_insert_token = None

    try:
        db_insert_token = db_user.yandex_disk_token.get_insert_token()
    except Exception:
        raise LinkExpired()

    if (incoming_insert_token != db_insert_token):
        raise InvalidInsertToken()

    return db_user
