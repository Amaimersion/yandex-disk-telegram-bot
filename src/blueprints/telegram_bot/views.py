from flask import (
    Blueprint,
    request,
    g,
    abort,
    render_template
)

from . import commands
from . import response


bp = Blueprint(
    "telegram_bot",
    __name__
)


@bp.route("/webhook", methods=["POST"])
def webhook():
    """
    Handles Webhook POST request from Telegram server.

    For Webhook we always should return 200 to indicate
    that we successfully got an update, otherwise Telegram
    will flood the server. So, not use `abort()` or anything.
    """
    data = request.get_json(
        force=True,
        silent=True,
        cache=False
    )

    if (data is None):
        return response.error()

    if (not data_is_valid(data)):
        return response.error()

    message = get_message(data)

    if (not message_is_valid(message)):
        return response.error()

    g.message = message
    g.user = message["from"]
    g.chat = message["chat"]

    entities = get_entities(message)
    message_text = message["text"]
    command = get_command(entities, message_text)

    route_command(command)

    return response.success()


def data_is_valid(data: dict) -> bool:
    """
    Checks submitted data for correctness.
    """
    return (
        isinstance(
            data.get("update_id"),
            int
        ) and
        (
            isinstance(
                data.get("message"),
                dict
            ) or
            isinstance(
                data.get("edited_message"),
                dict
            )
        )
    )


def get_message(data: dict) -> dict:
    """
    Extracts user message from submitted data.
    """
    return (
        data.get("message") or
        data.get("edited_message")
    )


def message_is_valid(message: dict) -> bool:
    """
    Checks extracted message for correctness.
    """
    return (
        isinstance(
            message.get("message_id"),
            int
        ) and
        isinstance(
            message.get("from"),
            dict
        ) and
        isinstance(
            message["from"].get("id"),
            int
        ) and
        isinstance(
            message.get("chat"),
            dict
        ) and
        isinstance(
            message["chat"].get("id"),
            int
        ) and
        isinstance(
            message["chat"].get("type"),
            str
        ) and
        isinstance(
            message.get("text"),
            str
        )
    )


def get_entities(message: dict) -> list:
    """
    Extracts entities from a message.
    """
    return (
        message.get("entities") or
        message.get("caption_entities") or
        []
    )


def entity_is_valid(entity: dict) -> bool:
    """
    Checks single entity for correctness.
    """
    return (
        isinstance(
            entity.get("type"),
            str
        ) and
        isinstance(
            entity.get("offset"),
            int
        ) and
        isinstance(
            entity.get("length"),
            int
        )
    )


def get_command(entities: list, message_text: str, default="/help") -> str:
    """
    Extracts bot command from entities.

    Note: first command will be returned, even if the list
    contains more than one command.

    :param entities: Message entities.
    :param message_text: Message text.
    :param default: Default command which will be returned if
    in message no any bot commands.
    """
    command = default

    for entity in entities:
        if (not entity_is_valid(entity)):
            continue

        if (not entity["type"] == "bot_command"):
            continue

        offset = entity["offset"]
        length = entity["length"]
        command = message_text[offset:offset + length]

        # ignore next commands
        break

    return command


def route_command(command: str) -> None:
    """
    Routes command to specific handler.
    """
    routes = {
        "/start": commands.help_handler,
        "/help": commands.help_handler,
        "/about": commands.about_handler,
        "/yandex_disk_auth": commands.yd_auth_handler
    }
    method = routes.get(command, commands.unknown_handler)

    method()


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
        "telegram_bot/yd_auth/error.html",
        error_title=error_info.get("title"),
        error_description=error_info.get("description"),
        raw_error_title=error,
        raw_error_description=error_description
    )


def handle_success():
    return "success"
