from flask import (
    Blueprint,
    request,
    abort
)


bp = Blueprint(
    "telegram_bot",
    __name__
)


@bp.route("/", methods=["POST"], strict_slashes=False)
def index():
    """
    Handles POST request from Telegram server.
    """
    data = request.get_json(
        force=True,
        silent=True,
        cache=False
    )

    if (data is None):
        abort(400)

    if (not data_is_valid(data)):
        abort(400)

    message = get_message(data)

    if (not message_is_valid(message)):
        abort(400)

    entities = get_entities(message)
    message_text = message["text"]
    command = get_command(entities, message_text)

    return {
        "method": "sendMessage",
        "chat_id": message["chat"]["id"],
        "text": "Success %s" % command
    }


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
                data.get("channel_post"),
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
        data.get("channel_post")
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
            message.get("text"),
            str
        ) and
        (
            isinstance(
                message.get("entities"),
                list
            ) or
            isinstance(
                message.get("caption_entities"),
                list
            )
        )
    )


def get_entities(message: dict) -> list:
    """
    Extracts entities from a message.
    """
    return (
        message.get("entities") or
        message.get("caption_entities")
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
