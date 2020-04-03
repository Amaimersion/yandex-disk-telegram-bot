from datetime import datetime, timezone

from flask import (
    request,
    abort,
    render_template,
    current_app
)
import jwt

from ....db import db, UserQuery, ChatQuery
from ....api import yandex, telegram
from .. import telegram_bot_blueprint as bp


TEMPLATES = {
    "error": "telegram_bot/yandex_disk_auth/error.html",
    "success": "telegram_bot/yandex_disk_auth/success.html",
}


@bp.route("/yandex_disk_authorization", methods=["GET"])
def yandex_disk_auth():
    if (is_error_request()):
        return handle_error()
    elif (is_success_request()):
        return handle_success()
    else:
        abort(400)


def is_error_request():
    state = request.args.get("state")
    error = request.args.get("error")

    return (
        isinstance(state, str) and
        len(state) > 0 and
        isinstance(error, str) and
        len(error) > 0
    )


def is_success_request():
    state = request.args.get("state")
    code = request.args.get("code")

    return (
        isinstance(state, str) and
        len(state) > 0 and
        isinstance(code, str) and
        len(code) > 0
    )


def handle_error():
    # TODO: remove user insert token.

    error = request.args.get("error")
    error_description = request.args.get("error_description")
    errors = {
        "access_denied": {
            "title": "Access Denied",
            "description": "You denied the access to Yandex.Disk."
        },
        "unauthorized_client": {
            "title": "Application is unavailable",
            "description": (
                "There is a problems with the application. "
                "Try later please."
            )
        }
    }
    error_info = errors.get(error, {})

    return render_template(
        TEMPLATES["error"],
        error_title=error_info.get("title"),
        error_description=error_info.get("description"),
        raw_error_title=error,
        raw_error_description=error_description
    )


def handle_success():
    errors = {
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
                "Some error occured on server side. "
                "Try later please."
            )
        }
    }
    encoded_state = request.args["state"]
    decoded_state = None

    try:
        decoded_state = jwt.decode(
            encoded_state,
            current_app.secret_key.encode(),
            algorithm="HS256"
        )
    except Exception:
        return render_template(
            TEMPLATES["error"],
            error_title=errors["invalid_credentials"]["title"],
            error_description=errors["invalid_credentials"]["description"]
        )

    incoming_user_id = decoded_state.get("user_id")
    incoming_insert_token = decoded_state.get("insert_token")

    if (
        incoming_user_id is None or
        incoming_insert_token is None
    ):
        return render_template(
            TEMPLATES["error"],
            error_title=errors["invalid_credentials"]["title"],
            error_description=errors["invalid_credentials"]["description"]
        )

    db_user = UserQuery.get_user_by_id(int(incoming_user_id))

    if (
        db_user is None or
        db_user.yandex_disk_token is None
    ):
        return render_template(
            TEMPLATES["error"],
            error_title=errors["invalid_credentials"]["title"],
            error_description=errors["invalid_credentials"]["description"]
        )

    db_insert_token = None

    try:
        db_insert_token = db_user.yandex_disk_token.get_insert_token()
    except Exception:
        return render_template(
            TEMPLATES["error"],
            error_title=errors["link_expired"]["title"],
            error_description=errors["link_expired"]["description"]
        )

    if (incoming_insert_token != db_insert_token):
        return render_template(
            TEMPLATES["error"],
            error_title=errors["invalid_insert_token"]["title"],
            error_description=errors["invalid_insert_token"]["description"]
        )

    code = request.args["code"]
    yandex_response = None

    try:
        yandex_response = yandex.get_access_token(
            grant_type="authorization_code",
            code=code
        )
    except Exception:
        return render_template(
            TEMPLATES["error"],
            error_title=errors["internal_server_error"]["title"],
            error_description=errors["internal_server_error"]["description"]
        )

    if ("error" in yandex_response):
        db_user.yandex_disk_token.clear_all_tokens()
        db.session.commit()

        return render_template(
            TEMPLATES["error"],
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
        current_datetime = datetime.now(timezone.utc)
        current_date = current_datetime.strftime("%d.%m.%Y")
        current_time = current_datetime.strftime("%H:%M:%S")
        current_timezone = current_datetime.strftime("%Z")

        telegram.send_message(
            chat_id=private_chat.telegram_id,
            parse_mode="HTML",
            text=(
                "<b>Access to Yandex.Disk Granted</b>"
                "\n\n"
                "Access was attached to your account "
                f"on {current_date} at {current_time} {current_timezone}."
                "\n\n"
                "If it wasn't you, you can detach this access with "
                "/yandex_disk_revoke"
            )
        )

    return render_template(
        TEMPLATES["success"]
    )
