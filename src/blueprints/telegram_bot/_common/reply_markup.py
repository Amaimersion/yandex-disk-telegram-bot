from typing import List, Any

from src.blueprints._common.utils import get_str_bytes_length
from src.blueprints.telegram_bot.webhook.dispatcher_interface import (
    CallbackQueryDispatcherData
)
from .command_names import CommandName
from .telegram_interface import (
    CallbackQuery as TelegramCallbackQuery
)


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
    result = TelegramCallbackQuery.serialize_data(
        CallbackQueryDispatcherData.encode_data(
            handler_names=handler_names,
            payload=payload
        )
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
