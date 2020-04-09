from typing import Union

from flask import (
    request,
    g,
    make_response
)

from .. import telegram_bot_blueprint as bp
from . import commands
from .commands.common.names import CommandNames


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
        return error_response()

    if (not data_is_valid(data)):
        return error_response()

    message = get_message(data)

    if (not message_is_valid(message)):
        return error_response()

    g.route_to = route_command
    g.incoming_message = message
    g.incoming_user = message["from"]
    g.incoming_chat = message["chat"]

    entities = get_entities(message)
    message_text = get_text(message)
    command = None

    if (message_text):
        command = get_command(entities, message_text)
    else:
        command = guess_command(message)

    route_command(command)

    return success_response()


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
        )
    )


def get_text(message: dict) -> str:
    """
    Extracts text from a message.
    """
    return (
        message.get("text") or
        message.get("caption") or
        ""
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


def get_command(
    entities: list,
    message_text: str,
    default=CommandNames.HELP
) -> str:
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


def guess_command(message: dict, default=CommandNames.HELP) -> str:
    """
    Tries to guess which command user assumed based on message.
    """
    command = default

    if ("photo" in message):
        command = CommandNames.UPLOAD_PHOTO
    elif ("document" in message):
        command = CommandNames.UPLOAD_FILE

    return command


def route_command(command: Union[str, CommandNames]) -> None:
    """
    Routes command to specific handler.
    """
    if (isinstance(command, CommandNames)):
        command = command.value

    routes = {
        CommandNames.START.value: commands.help_handler,
        CommandNames.HELP.value: commands.help_handler,
        CommandNames.ABOUT.value: commands.about_handler,
        CommandNames.SETTINGS.value: commands.settings_handler,
        CommandNames.YD_AUTH.value: commands.yd_auth_handler,
        CommandNames.YD_REVOKE.value: commands.yd_revoke_handler,
        CommandNames.UPLOAD_PHOTO.value: commands.upload_photo_handler,
        CommandNames.UPLOAD_FILE.value: commands.upload_file_handler,
        CommandNames.UPLOAD_AUDIO.value: commands.upload_audio_handler,
        CommandNames.CREATE_FOLDER.value: commands.create_folder_handler
    }
    method = routes.get(command, commands.unknown_handler)

    method()


def error_response():
    """
    Creates error response for Telegram Webhook.
    """
    return make_response((
        {
            "ok": False,
            "error_code": 400
        },
        200
    ))


def success_response():
    """
    Creates success response for Telegram Webhook.
    """
    return make_response((
        {
            "ok": True
        },
        200
    ))
