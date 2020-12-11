"""
This code directly related to dispatcher (`dispatcher.py`).
However, it was extracted into separate file to
avoid circular imports.

Many handlers using `DispatcherEvent`. Howerver, dispatcher
itself imports these handlers. So, circular import occurs.
Handlers may import entire dispatcher module, not only enum
(`import dispatcher`). But i don't like this approach, so,
dispatcher events were extracted into separate file.
Same logic for another enums.
"""


from enum import Enum, auto


class StringAutoName(Enum):
    """
    `auto()` will return strings, not ints.
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
