from flask import (
    request,
    abort,
    render_template,
    current_app
)
import jwt

from ....db import UserQuery
from .. import telegram_bot_blueprint as bp


TEMPLATES = {
    "error": "telegram_bot/yandex_disk_auth/error.html"
}


@bp.route("/yandex_disk_auth", methods=["GET"])
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
    return "success"
