"""
Used for implementing of stateful dialog between the bot and user
on Telegram chats. It is just manages the state and data, so, this
module should work in pair with dispatcher that will route messages
based on current state, data and some custom conditions. In short,
this module manages the state and dispatcher manages the behavior,
dispatcher should be implemented independently.

- requires Redis to be enabled. Use `stateful_chat_is_enabled()`
to check if stateful chat is enabled and can be used.
- you shouldn't import things that starts with `_`,
because they are intended for internal usage only

Documentation for this entire module will be provided here, not in every
function documentation. This documentation tells the dispatcher how this
should be implemented, however, dispatcher can change final realization,
so, also take a look at dispatcher documentation for how to use this module.

- each function can raise an error if it occurs

"Custom Data" functions.

Using set/get/delete_<namespace> you can manage your own data in
specific namespace. Instead of `update` operation use `set` operation.
For example, `set_user_data` sets/updates your custom data in user namespace,
that potentially can be used to store data about specific user across
multiple chats. `user` argument provides unique user identificator, as
id or name. `expire` argument tells if this data should be deletde after
given number of seconds, `0` is used for permanent storing.
Documentation for different namespaces (user, user in chat, chat, etc.)
is similar.

"Event Handling" functions.

"Disposable handler" means that only one handler will exists
at a time, and that handler should handle an event only one time.
For example, you can set handler for `TEXT` event, and when message with
text will arrive, this handler will be called for that message. Next time,
when text messages arrives, this handler will be not called, because
it already was called for previous message.
There can be only one handler, so, calling `set_disposable_handler` at
first in function № 1, then in function № 2, and after in function № 3
will set only handler from function № 3, because last call from № 3 will
override handler from № 2, and call from № 2 will override handler from № 1.
You should specify set of events, not single event. Dispatcher should
implement the logic for how events of both handler and message are compared.
Dispatcher also should implement deleting of handler when it about to call.
It is recommended to stick with documeneted logic.
`user`, `chat`, `handler` - unique identifiers of these objects, such as
id's or names.
`expire` - means handler will be automatically deleted after given number
of seconds. `0` means it is permanent handler that will wait for it call.
If you call register function again for same handler, then old timeout
will be removed, and new one with this value will be setted.
`events` - iterable of unique events for that dispatcher.
Note: if you want to use `Enum`, then pass values of that enum, not
objects itself. Redis will return back strings even if you will pass
int values, so, be aware of it when comparing these values.
Note: return result is an unordered. So, you shouldn't rely on order.

"Subscribed handlers" means you can register any amount of handlers for
any events, these handlers will be called every time until you remove them.
For example, you can register handler № 1 for TEXT and URL event, and
register handler № 2 for TEXT and PHOTO event. Realization of routing
is up to dispatcher, but recommend way is to route message (TEXT) to both
handler № 1 and handler № 2, route message (TEXT, PHOTO) to both
handler № 1 and handler № 2, and route message (URL) to handler № 1.
Documentation of function arguments is same as for "disposable handler".
Note: these handlers stored in a set, so, you can safely call register
function which registers same handler from different functions, and result
will be one registered handler.
"""


from collections import deque
from typing import Union, Set

from src.extensions import redis_client


# region Common


# Namespaces
_SEPARATOR = ":"
_NAMESPACE_KEY = "stateful_chat"
_USER_KEY = "user"
_CHAT_KEY = "chat"
_DATA_KEY = "custom_data"
_DISPOSABLE_HANDLER_KEY = "disposable_handler"
_NAME_KEY = "name"
_EVENTS_KEY = "events"
_SUBSCRIBED_HANDLERS_KEY = "subscribed_handlers"


def _create_key(*args) -> str:
    return _SEPARATOR.join(map(str, args))


def stateful_chat_is_enabled() -> bool:
    return redis_client.is_enabled


# endregion


# region Custom Data


def _set_data(
    key: str,
    field: str,
    value: str,
    expire: int
) -> None:
    key = _create_key(_NAMESPACE_KEY, key, _DATA_KEY, field)
    pipeline = redis_client.pipeline()

    pipeline.set(key, value)

    if (expire > 0):
        pipeline.expire(key, expire)

    pipeline.execute(raise_on_error=True)


def _get_data(
    key: str,
    field: str
) -> Union[str, None]:
    return redis_client.get(
        _create_key(_NAMESPACE_KEY, key, _DATA_KEY, field)
    )


def _delete_data(
    key: str,
    field: str
) -> None:
    redis_client.delete(
        _create_key(_NAMESPACE_KEY, key, _DATA_KEY, field)
    )


def set_user_data(
    user: str,
    key: str,
    value: str,
    expire: int = 0
) -> None:
    _set_data(
        _create_key(_USER_KEY, user),
        key,
        value,
        expire
    )


def get_user_data(
    user: str,
    key: str
):
    return _get_data(
        _create_key(_USER_KEY, user),
        key
    )


def delete_user_data(
    user: str,
    key: str
) -> None:
    _delete_data(
        _create_key(_USER_KEY, user),
        key
    )


def set_user_chat_data(
    user: str,
    chat: str,
    key: str,
    value: str,
    expire: int = 0
) -> None:
    _set_data(
        _create_key(_USER_KEY, user, _CHAT_KEY, chat),
        key,
        value,
        expire
    )


def get_user_chat_data(
    user: str,
    chat: str,
    key: str
):
    return _get_data(
        _create_key(_USER_KEY, user, _CHAT_KEY, chat),
        key
    )


def delete_user_chat_data(
    user: str,
    chat: str,
    key: str
) -> None:
    _delete_data(
        _create_key(_USER_KEY, user, _CHAT_KEY, chat),
        key
    )


def set_chat_data(
    chat: str,
    key: str,
    value: str,
    expire: int = 0
) -> None:
    _set_data(
        _create_key(_CHAT_KEY, chat),
        key,
        value,
        expire
    )


def get_chat_data(
    chat: str,
    key: str
):
    return _get_data(
        _create_key(_CHAT_KEY, chat),
        key
    )


def delete_chat_data(
    chat: str,
    key: str
) -> None:
    _delete_data(
        _create_key(_CHAT_KEY, chat),
        key
    )


# endregion


# region Event Handling


def set_disposable_handler(
    user: str,
    chat: str,
    handler: str,
    events: Set[str],
    expire: int = 0
) -> None:
    name_key = _create_key(
        _NAMESPACE_KEY,
        _USER_KEY,
        user,
        _CHAT_KEY,
        chat,
        _DISPOSABLE_HANDLER_KEY,
        _NAME_KEY
    )
    events_key = _create_key(
        _NAMESPACE_KEY,
        _USER_KEY,
        user,
        _CHAT_KEY,
        chat,
        _DISPOSABLE_HANDLER_KEY,
        _EVENTS_KEY
    )
    pipeline = redis_client.pipeline()

    pipeline.set(name_key, handler)
    # in case of update (same name for already
    # existing handler) we need to delete old events
    # in order to not merge them with new ones.
    # also, `sadd` don't clears expire, but
    # `delete` does
    pipeline.delete(events_key)
    pipeline.sadd(events_key, *events)

    if (expire > 0):
        pipeline.expire(name_key, expire)
        pipeline.expire(events_key, expire)

    pipeline.execute(raise_on_error=True)


def get_disposable_handler(
    user: str,
    chat: str
) -> Union[dict, None]:
    name_key = _create_key(
        _NAMESPACE_KEY,
        _USER_KEY,
        user,
        _CHAT_KEY,
        chat,
        _DISPOSABLE_HANDLER_KEY,
        _NAME_KEY
    )
    events_key = _create_key(
        _NAMESPACE_KEY,
        _USER_KEY,
        user,
        _CHAT_KEY,
        chat,
        _DISPOSABLE_HANDLER_KEY,
        _EVENTS_KEY
    )
    pipeline = redis_client.pipeline()

    pipeline.get(name_key)
    pipeline.smembers(events_key)

    name, events = pipeline.execute(raise_on_error=True)
    result = None

    if name:
        result = {
            "name": name,
            "events": events
        }

    return result


def delete_disposable_handler(
    user: str,
    chat: str
) -> None:
    name_key = _create_key(
        _NAMESPACE_KEY,
        _USER_KEY,
        user,
        _CHAT_KEY,
        chat,
        _DISPOSABLE_HANDLER_KEY,
        _NAME_KEY
    )
    events_key = _create_key(
        _NAMESPACE_KEY,
        _USER_KEY,
        user,
        _CHAT_KEY,
        chat,
        _DISPOSABLE_HANDLER_KEY,
        _EVENTS_KEY
    )
    pipeline = redis_client.pipeline()

    pipeline.delete(name_key)
    pipeline.delete(events_key)

    pipeline.execute(raise_on_error=True)


def subscribe_handler(
    user: str,
    chat: str,
    handler: str,
    events: Set[str],
    expire: int = 0
) -> None:
    # In this set stored all handler names
    # that were registered. It is not indicator
    # if handler is registered at the moment of check.
    subscribed_handlers_key = _create_key(
        _NAMESPACE_KEY,
        _USER_KEY,
        user,
        _CHAT_KEY,
        chat,
        _SUBSCRIBED_HANDLERS_KEY
    )
    # Example - `...:<handler_name>:events`.
    # In this set stored all events for this handler.
    # If `events_key` doesn't exists or empty, then it is
    # indicates that handler not registered anymore and
    # should be removed from `subscribed_handlers_key`.
    events_key = _create_key(
        _NAMESPACE_KEY,
        _USER_KEY,
        user,
        _CHAT_KEY,
        chat,
        _SUBSCRIBED_HANDLERS_KEY,
        handler,
        _EVENTS_KEY
    )
    pipeline = redis_client.pipeline()

    pipeline.sadd(subscribed_handlers_key, handler)
    # in case of update (same name for already
    # existing handler) we need to delete old events
    # in order to not merge them with new ones.
    # also, `sadd` don't clears expire, but
    # `delete` does
    pipeline.delete(events_key)
    pipeline.sadd(events_key, *events)

    if (expire > 0):
        pipeline.expire(events_key)

    pipeline.execute(raise_on_error=True)


def unsubcribe_handler(
    user: str,
    chat: str,
    handler: str
) -> None:
    subscribed_handlers_key = _create_key(
        _NAMESPACE_KEY,
        _USER_KEY,
        user,
        _CHAT_KEY,
        chat,
        _SUBSCRIBED_HANDLERS_KEY
    )
    events_key = _create_key(
        _NAMESPACE_KEY,
        _USER_KEY,
        user,
        _CHAT_KEY,
        chat,
        _SUBSCRIBED_HANDLERS_KEY,
        handler,
        _EVENTS_KEY
    )
    pipeline = redis_client.pipeline()

    pipeline.srem(subscribed_handlers_key, handler)
    pipeline.delete(events_key)

    pipeline.execute(raise_on_error=True)


def get_subscribed_handlers(
    user: str,
    chat: str
) -> deque:
    subscribed_handlers_key = _create_key(
        _NAMESPACE_KEY,
        _USER_KEY,
        user,
        _CHAT_KEY,
        chat,
        _SUBSCRIBED_HANDLERS_KEY
    )
    possible_handlers = redis_client.smembers(
        subscribed_handlers_key
    )
    pipeline = redis_client.pipeline()

    for possible_handler in possible_handlers:
        pipeline.smembers(
            _create_key(
                _NAMESPACE_KEY,
                _USER_KEY,
                user,
                _CHAT_KEY,
                chat,
                _SUBSCRIBED_HANDLERS_KEY,
                possible_handler,
                _EVENTS_KEY
            )
        )

    events = pipeline.execute(raise_on_error=True)
    subscribed_handlers = deque()
    i = 0

    # `possible_handlers` is a set.
    # Set it is an unordered structure, so, order
    # of iteration not guaranted from time to time
    # (for example, from first script execution to second
    # script execution).
    # However, in Python order of set iteration in
    # single run is a same (if set wasn't modified),
    # so, we can safely iterate this set one more time
    # and associate it values with another values
    # through `i` counter (`events` is an array).
    # See for more: https://stackoverflow.com/q/3848091/8445442
    for handler_name in possible_handlers:
        handler_events = events[i]
        i += 1

        # see `subscribe_handler` documentation for
        # why this check works so
        if handler_events:
            subscribed_handlers.append({
                "name": handler_name,
                "events": handler_events
            })
        else:
            unsubcribe_handler(user, chat, handler_name)

    return subscribed_handlers


# endregion
