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
    data = request.get_json(
        force=True,
        silent=True,
        cache=False
    )

    if (data is None):
        abort(400)

    message_is_valid = (
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

    if (not message_is_valid):
        abort(400)

    message = data["message"] or data["channel_post"]

    message_2_is_valid = (
        isinstance(
            message.get("from"),
            dict
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

    if (not message_2_is_valid):
        abort(400)

    print(message)

    return "Hello!"
