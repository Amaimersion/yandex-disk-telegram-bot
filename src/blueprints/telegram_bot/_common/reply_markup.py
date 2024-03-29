from typing import List, Any

from flask import current_app

from src.blueprints._common.utils import get_str_bytes_length
from src.blueprints.telegram_bot.webhook.dispatcher_interface import (
    CallbackQueryDispatcherData
)
from .command_names import CommandName
from .telegram_interface import (
    CallbackQuery as TelegramCallbackQuery
)


# Use this value if you don't want to send any payload
EMPTY_PAYLOAD = CallbackQueryDispatcherData.empty_payload


class TooBigCallbackDataError(Exception):
    """
    - https://core.telegram.org/bots/api#inlinekeyboardbutton
    """
    pass


def create_callback_data(
    handler_names: List[CommandName],
    payload: Any
) -> str:
    """
    - don't interact with returned value directly

    :param handler_names:
    Dispatcher will dispatch subsequent callback requests
    with this `payload` to these handlers.
    :param payload:
    Any additional data which should go along with
    callback requests. Any serializable value is accepted.

    :returns:
    Value that can be used for `callback_data` property.

    :raises:
    `TooBigCallbackDataError` in case if result
    value is too big (at the moment maximum result
    size is 64 bytes). Try to reduce payload length:
    use int enums, not string ones; simplify strings, etc.
    If your payload is really big, then you may need to use
    `stateful_chat` module.
    """
    dispatcher_data = CallbackQueryDispatcherData.encode_data(
        handler_names=handler_names,
        payload=payload
    )
    result = TelegramCallbackQuery.serialize_data(dispatcher_data)

    current_app.logger.debug(
        f"{handler_names} and {payload} were encoded into {dispatcher_data}"
    )

    bytes_length = get_str_bytes_length(result)
    max_bytes_length = 64
    too_big = (bytes_length > max_bytes_length)

    if too_big:
        raise TooBigCallbackDataError(
            f"Result size - {bytes_length} bytes. "
            f"Maximum size - {max_bytes_length} bytes."
        )

    return result
