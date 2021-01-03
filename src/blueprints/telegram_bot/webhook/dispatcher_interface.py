"""
This code directly related to dispatcher (`dispatcher.py`).
However, it was extracted into separate file to avoid circular imports.

Many handlers using `DispatcherEvent`. Howerver, dispatcher
itself imports these handlers. So, circular import occurs.
Handlers may import entire dispatcher module, not only enum
(`import dispatcher`). But i don't like this approach, so,
dispatcher events were extracted into separate file.
Same logic for another interfaces.
"""


from enum import Enum, auto
from typing import (
    List,
    Any
)

from src.blueprints.telegram_bot._common.command_names import CommandName


class StringAutoName(Enum):
    """
    `auto()` will return strings, not int's.
    """
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return str(count)


class DispatcherEvent(StringAutoName):
    """
    An event that was detected and fired by dispatcher.

    These events is primarily for Telegram messages.
    Note: there can be multiple events in one message,
    so, you always should operate with list of events,
    not single event (instead you can use list with one element).

    Note: values of that enums are strings, not ints.
    It is because it is expected that these values will be
    compared with Redis values in future. Redis by default
    returns strings.
    """
    # Nothing of known events is detected
    NONE = auto()
    # Message contains plain text (non empty)
    PLAIN_TEXT = auto()
    PHOTO = auto()
    VIDEO = auto()
    FILE = auto()
    AUDIO = auto()
    VOICE = auto()
    BOT_COMMAND = auto()
    URL = auto()
    HASHTAG = auto()
    EMAIL = auto()


class RouteSource(Enum):
    """
    Who initiated the route to a handler.

    For example, `DISPOSABLE_HANDLER` means a handler was
    called because of `set_disposable_handler()` from
    stateful chat module.
    """
    DISPOSABLE_HANDLER = auto()
    SUBSCRIBED_HANDLER = auto()
    SAME_DATE_COMMAND = auto()
    DIRECT_COMMAND = auto()
    GUESSED_COMMAND = auto()
    CALLBACK_QUERY_DATA = auto()


class CallbackQueryDispatcherData:
    """
    Dispatcher interface for data of callback query.

    Data is a `dict` with following keys:
    - `handler_names`: names of handlers that should
    handle current data;
    - `payload`: arbitrary data for every handler.

    So, you should use `encode_data` and `decode_data`
    in order dispatcher was able to create a route
    for incoming callback data.

    NOTE:
    keep in mind that Telegram can have a length limit
    for callback data.
    """
    # keep length of these keys as small as possible,
    # because Telegram have length limit for callback data
    handler_names_key = "H"
    payload_key = "P"
    empty_payload = None

    @staticmethod
    def encode_data(
        handler_names: List[CommandName],
        payload: Any
    ) -> dict:
        handler_names_key = CallbackQueryDispatcherData.handler_names_key
        payload_key = CallbackQueryDispatcherData.payload_key
        empty_payload = CallbackQueryDispatcherData.empty_payload
        result = {}
        handler_names_indexes = []

        for handler_name in handler_names:
            index = CommandName.get_index(handler_name.value)

            if index is None:
                raise Exception(f"Unknown handler name - {handler_name}")
            else:
                handler_names_indexes.append(index)

        result[handler_names_key] = handler_names_indexes

        if (payload != empty_payload):
            result[payload_key] = payload

        return result

    @staticmethod
    def decode_data(data: dict) -> dict:
        handler_names_key = CallbackQueryDispatcherData.handler_names_key
        payload_key = CallbackQueryDispatcherData.payload_key
        handler_names_raw_data = data.get(handler_names_key)
        handler_names = []

        for index in handler_names_raw_data:
            if isinstance(index, int):
                handler_name = CommandName.get_name(index)

                if handler_name is not None:
                    handler_names.append(handler_name)

        return {
            "handler_names": handler_names,
            "payload": data.get(payload_key)
        }

    @staticmethod
    def data_is_valid(data: dict) -> bool:
        handler_names_key = CallbackQueryDispatcherData.handler_names_key

        return (
            isinstance(
                data,
                dict
            ) and
            isinstance(
                data.get(handler_names_key),
                list
            )
        )
