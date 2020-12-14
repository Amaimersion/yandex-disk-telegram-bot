from flask import (
    request,
    abort,
    render_template
)

from src.api import telegram
from src.database import ChatQuery
from src.blueprints._common.utils import get_current_datetime
from src.blueprints.telegram_bot import telegram_bot_blueprint as bp
from src.blueprints.telegram_bot._common import yandex_oauth
from src.blueprints.telegram_bot._common.command_names import CommandName


@bp.route("/yandex_disk_authorization")
def yd_auth():
    """
    Handles user redirect from Yandex.OAuth page
    (Auto Code method).
    """
    if is_success_request():
        return handle_success()
    elif is_error_request():
        return handle_error()
    else:
        abort(400)


def is_success_request() -> bool:
    """
    :returns:
    Incoming request is a successful user authorization.
    """
    state = request.args.get("state", "")
    code = request.args.get("code", "")

    return (
        len(state) > 0 and
        len(code) > 0
    )


def is_error_request() -> bool:
    """
    :returns:
    Incoming request is a failed user authorization.
    """
    state = request.args.get("state", "")
    error = request.args.get("error", "")

    return (
        len(state) > 0 and
        len(error) > 0
    )


def handle_success():
    """
    Handles success user authorization.
    """
    state = request.args["state"]
    code = request.args["code"]
    client = yandex_oauth.YandexOAuthAutoCodeClient()
    result = None

    try:
        result = client.after_success_redirect(state, code)
    except yandex_oauth.InvalidState:
        return create_error_response("invalid_credentials")
    except yandex_oauth.ExpiredInsertToken:
        return create_error_response("link_expired")
    except yandex_oauth.InvalidInsertToken:
        return create_error_response("invalid_insert_token")
    except Exception as error:
        print(error)
        return create_error_response("internal_server_error")

    if not result["ok"]:
        return create_error_response(
            error_code="internal_server_error",
            raw_error_title=result["error"],
            raw_error_description=result.get("error_description")
        )

    user = result["user"]
    private_chat = ChatQuery.get_private_chat(user.id)

    if private_chat:
        now = get_current_datetime()
        date = now["date"]
        time = now["time"]
        timezone = now["timezone"]

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


def handle_error():
    """
    Handles failed user authorization.
    """
    state = request.args["state"]
    client = yandex_oauth.YandexOAuthAutoCodeClient()

    try:
        client.after_error_redirect(state)
    except Exception:
        # we do not care about any errors at that stage
        pass

    return create_error_response()


def create_success_response():
    """
    :returns:
    Rendered template for success page.
    """
    return render_template(
        "telegram_bot/yd_auth/success.html"
    )


def create_error_response(
    error_code: str = None,
    raw_error_title: str = None,
    raw_error_description: str = None
):
    """
    :param error_code:
    Name of error for user friendly information.
    If not specified, then defaults to
    `error` argument from request.
    :param raw_error_title:
    Raw error title for debugging purposes.
    If not specified, then defaults to
    `error_code` argument.
    :param raw_error_description:
    Raw error description for debugging purposes.
    If not specified, then defaults to
    `error_description` argument from request.

    :returns:
    Rendered template for error page.
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
                "There is a problems with me. "
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

    if error_code is None:
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
