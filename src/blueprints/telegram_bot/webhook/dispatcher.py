from typing import (
    Union,
    Callable,
    Set
)
from collections import deque
import traceback

from flask import current_app
from src.blueprints.telegram_bot._common.stateful_chat import (
    stateful_chat_is_enabled,
    get_disposable_handler,
    delete_disposable_handler,
    get_subscribed_handlers,
    set_user_chat_data,
    get_user_chat_data
)
from src.blueprints.telegram_bot._common.telegram_interface import (
    Update as TelegramUpdate,
    Message as TelegramMessage,
    CallbackQuery as TelegramCallbackQuery
)
from src.blueprints.telegram_bot._common.command_names import CommandName
from . import commands
from .dispatcher_interface import (
    DispatcherEvent,
    RouteSource,
    CallbackQueryDispatcherData
)


class IntellectualDispatchResult:
    """
    Result of intellectual dispatch that can be used
    to route a Telegram update request.
    """
    def __init__(self):
        # Each handler from that array will get its own dispatch.
        # Specify name as `Union[CommandName, str]`.
        # Order is matters
        self.handler_names = deque()

        # Who initiated a route to that handler.
        # If you specify at least one handler, then
        # you MUST specify route source
        self.route_source = None

        # Pass any additional `kwargs` for each handler
        self.kwargs = {}

    def create_handler(self) -> Callable:
        """
        Creates handler that will handle this dispatch.

        - creates separate handlers for each one from `self.handler_names`
        - it is guaranteed that these parameters will be passed for
        each handler through `kwargs`: `route_source`
        - you can add your own `kwargs` through `self.kwargs`

        :returns:
        It is guaranteed that this handler will
        not raise any exceptions. Function arguments
        already configured, but you can provide your
        own through `*args` and `**kwargs`.
        You should  call this returned function in order
        to run all handlers (there can be multiple handlers
        that will handle current route).

        :raises:
        If at least one handler exists and there is no valid
        `self.route_source`, then error will be thrown, because
        `self.route_source` is mandatory.
        """
        if len(self.handler_names):
            if self.route_source is None:
                raise Exception("Route source is unknown")

        def method(*args, **kwargs):
            for handler_name in self.handler_names:
                handler_method = direct_dispatch(handler_name)

                try:
                    handler_method(
                        *args,
                        **kwargs,
                        **self.kwargs,
                        route_source=self.route_source
                    )
                except Exception as error:
                    print(
                        f"{handler_name}: {error}",
                        "\n",
                        traceback.format_exc()
                    )

        return method


def intellectual_dispatch(update: TelegramUpdate) -> Union[Callable, None]:
    """
    Implements intellectual dispatch of Telegram update request.

    Strategy of dispatch:
    1) if message exists, then it will be dispatched
    2) if callback query exists, then it will be dispatched

    See documentation of these dispatch methods for additional strategy:
    - `message_dispatch`
    - `callback_query_dispatch`

    :returns:
    It is guaranteed that most appropriate callable handler that
    not raises an error will be returned. Function arguments already
    configured, but you can also provide your own through `*args`
    and `**kwargs`. Note that different dispatchers (message, callback query,
    etc.) provide different arguments, so, if `kwargs['property']` exists
    in dispatch result of one dispatch handler (message, for example), it
    may not exists in dispatch result of another dispatch handler
    (callback query, for example). You should call this function in order
    to run all handlers for that Telegram update (there can be multiple
    handlers in returned function). If unable to select handler for incoming
    Telegram update for some reason, then `None` will be returned.

    :raises:
    Raises an error if unable to route incoming Telegram update.
    """
    if not update.is_valid():
        return None

    message = update.get_message()
    callback_query = update.get_callback_query()
    dispatch_result = None

    if message:
        dispatch_result = message_dispatch(message)

    if (not dispatch_result and callback_query):
        dispatch_result = callback_query_dispatch(callback_query)

    if not dispatch_result:
        return None

    dispatch_result.kwargs["update"] = update
    handler = dispatch_result.create_handler()

    return handler


def message_dispatch(
    message: TelegramMessage
) -> Union[IntellectualDispatchResult, None]:
    """
    Intellectual dispatch to handlers of Telegram message.

    - provides support for stateful chat (if Redis is enabled).

    Strategy of dispatch:
    1) if disposable handler exists and message events matches,
    then only that handler will be called and after removed.
    That disposable handler will be associated with message date.
    2) if subscribed handlers exists, then only ones with events
    matched to message events will be called. If nothing is matched,
    then forwarding to № 3
    3) attempt to get first `bot_command` entity from message.
    It will be treated as direct command. That direct command will be
    associated with message date. If nothing found, then forwarding to № 4
    4) attempt to get command based on message date.
    For example, when `/upload_photo` was used for message that was
    sent on `1607677734` date, and after that separate message was
    sent on same `1607677734` date, then it is the case.
    If nothing found, then forwarding to № 5
    5) guessing of command that user assumed based on
    content of message

    If stateful chat not enabled, then № 1 and № 2 will be skipped.

    Events matching:
    - if at least one event matched, then that handler will be
    marked as "matched".

    Note: there can be multiple handlers selected for single message.
    Order of execution not determined.

    :param message:
    Incoming Telegram message.

    :returns:
    Dispatch result or `None` if unable to dispatch.
    """
    if not message.is_valid():
        return None

    user_id = message.get_user().id
    chat_id = message.get_chat().id
    message_date = int(message.get_date().timestamp())
    is_stateful_chat = stateful_chat_is_enabled()
    disposable_handler = None
    subscribed_handlers = None

    if is_stateful_chat:
        disposable_handler = get_disposable_handler(user_id, chat_id)
        subscribed_handlers = get_subscribed_handlers(user_id, chat_id)

    message_events = (
        detect_message_events(message) if (
            disposable_handler or
            subscribed_handlers
        ) else None
    )
    result = IntellectualDispatchResult()

    if disposable_handler:
        match = match_events(
            message_events,
            disposable_handler["events"]
        )

        if match:
            result.route_source = RouteSource.DISPOSABLE_HANDLER
            result.handler_names.append(disposable_handler["name"])

            delete_disposable_handler(user_id, chat_id)

    if (
        subscribed_handlers and
        not result.handler_names
    ):
        for handler in subscribed_handlers:
            match = match_events(
                message_events,
                handler["events"]
            )

            if match:
                result.route_source = RouteSource.SUBSCRIBED_HANDLER
                result.handler_names.append(handler["name"])

    if not result.handler_names:
        command = message.get_entity_value("bot_command")

        if command:
            result.route_source = RouteSource.DIRECT_COMMAND
            result.handler_names.append(command)

    should_bind_command_to_date = (
        is_stateful_chat and
        (
            result.route_source in
            (
                RouteSource.DISPOSABLE_HANDLER,
                RouteSource.DIRECT_COMMAND
            )
        )
    )
    should_get_command_by_date = (
        is_stateful_chat and
        not result.handler_names
    )

    if should_bind_command_to_date:
        # we expect only one active command
        command = result.handler_names[0]

        # we need to handle cases when user forwards
        # many separate messages (one with direct command and
        # others without any command but with some attachments).
        # These messages will be sended by Telegram one by one
        # (it is means we got separate direct command and
        # separate attachments without that any commands).
        # We also using `RouteSource.DISPOSABLE_HANDLER`
        # because user can start command without any attachments,
        # but forward multiple attachments at once or send
        # media group (media group messages have same date).
        bind_command_to_date(
            user_id,
            chat_id,
            message_date,
            command
        )
    elif should_get_command_by_date:
        command = get_command_by_date(
            user_id,
            chat_id,
            message_date
        )

        if command:
            result.route_source = RouteSource.SAME_DATE_COMMAND
            result.handler_names.append(command)

    if not result.handler_names:
        result.route_source = RouteSource.GUESSED_COMMAND
        result.handler_names.append(guess_message_command(message))

    result.kwargs["user_id"] = user_id
    result.kwargs["chat_id"] = chat_id
    result.kwargs["message"] = message
    result.kwargs["message_events"] = message_events

    return result


def callback_query_dispatch(
    callback_query: TelegramCallbackQuery
) -> Union[IntellectualDispatchResult, None]:
    """
    Intellectual dispatch to handlers of Telegram callback query.

    NOTE:
    you should use `CallbackQueryDispatcherData` interface to
    pass data in `data` property of callback query. Any other
    data format will be considered as invalid and will be rejected.

    Strategy of dispatch:
    1) read data and ensure it is valid
    2) direct dispatch to all handlers that
    specified under `handler_names` key

    :param callback_query:
    Incoming Telegram callback query.

    :returns:
    Dispatch result or `None` if unable to dispatch.
    """
    if not callback_query.is_valid():
        return None

    raw_data = None

    try:
        raw_data = callback_query.get_data()
    except Exception as error:
        print(error)
        return None

    if not CallbackQueryDispatcherData.data_is_valid(raw_data):
        return None

    data = CallbackQueryDispatcherData.decode_data(raw_data)
    handler_names = data["handler_names"]
    payload = data["payload"]
    user = callback_query.get_user()

    result = IntellectualDispatchResult()
    result.route_source = RouteSource.CALLBACK_QUERY_DATA
    result.handler_names.extend(handler_names)
    result.kwargs["user_id"] = user.id
    result.kwargs["callback_query"] = callback_query
    result.kwargs["callback_query_data"] = payload

    return result


def direct_dispatch(
    command: Union[CommandName, str],
    fallback: Callable = commands.unknown_handler
) -> Callable:
    """
    Direct dispatch to handler of the command.
    i.e., it doesn't uses any guessing or stateful chats,
    it is just direct route (command_name -> command_handler).

    :param command:
    Name of command to dispatch to.
    :param fallback:
    Fallback handler that will be used in case if command is unknown.

    :returns:
    It is guaranteed that some callable handler will be returned.
    It is handler for incoming command and you should call this.
    """
    if isinstance(command, CommandName):
        command = command.value

    routes = {
        CommandName.START.value: commands.help_handler,
        CommandName.HELP.value: commands.help_handler,
        CommandName.ABOUT.value: commands.about_handler,
        CommandName.SETTINGS.value: commands.settings_handler,
        CommandName.YD_AUTH.value: commands.yd_auth_handler,
        CommandName.YD_REVOKE.value: commands.yd_revoke_handler,
        CommandName.UPLOAD_PHOTO.value: commands.upload_photo_handler,
        CommandName.UPLOAD_FILE.value: commands.upload_file_handler,
        CommandName.UPLOAD_AUDIO.value: commands.upload_audio_handler,
        CommandName.UPLOAD_VIDEO.value: commands.upload_video_handler,
        CommandName.UPLOAD_VOICE.value: commands.upload_voice_handler,
        CommandName.UPLOAD_URL.value: commands.upload_url_handler,
        CommandName.PUBLIC_UPLOAD_PHOTO.value: commands.public_upload_photo_handler, # noqa
        CommandName.PUBLIC_UPLOAD_FILE.value: commands.public_upload_file_handler, # noqa
        CommandName.PUBLIC_UPLOAD_AUDIO.value: commands.public_upload_audio_handler, # noqa
        CommandName.PUBLIC_UPLOAD_VIDEO.value: commands.public_upload_video_handler, # noqa
        CommandName.PUBLIC_UPLOAD_VOICE.value: commands.public_upload_voice_handler, # noqa
        CommandName.PUBLIC_UPLOAD_URL.value: commands.public_upload_url_handler, # noqa
        CommandName.CREATE_FOLDER.value: commands.create_folder_handler,
        CommandName.PUBLISH.value: commands.publish_handler,
        CommandName.UNPUBLISH.value: commands.unpublish_handler,
        CommandName.SPACE_INFO.value: commands.space_info_handler,
        CommandName.ELEMENT_INFO.value: commands.element_info_handler,
        CommandName.DISK_INFO.value: commands.disk_info_handler,
        CommandName.COMMANDS_LIST.value: commands.commands_list_handler
    }
    handler = routes.get(command, fallback)

    def method(*args, **kwargs):
        handler(*args, **kwargs)

    return method


def guess_message_command(
    message: TelegramMessage,
    fallback: CommandName = CommandName.HELP
) -> str:
    """
    Tries to guess which bot command user
    assumed based on content of a message.

    :param fallback:
    Fallback command which will be returned if unable to guess.

    :returns:
    Guessed bot command name based on a message.
    """
    command = fallback
    raw_data = message.raw_data

    if ("photo" in raw_data):
        command = CommandName.UPLOAD_PHOTO
    elif ("document" in raw_data):
        command = CommandName.UPLOAD_FILE
    elif ("audio" in raw_data):
        command = CommandName.UPLOAD_AUDIO
    elif ("video" in raw_data):
        command = CommandName.UPLOAD_VIDEO
    elif ("voice" in raw_data):
        command = CommandName.UPLOAD_VOICE
    elif (message.get_entity_value("url") is not None):
        command = CommandName.UPLOAD_URL

    return command.value


def detect_message_events(
    message: TelegramMessage
) -> Set[str]:
    """
    :returns:
    Detected dispatcher events.
    See `DispatcherEvent` documentation for more.
    Note: it is strings values, because these values
    should be compared with Redis values, which is
    also strings.
    """
    events = set()
    entities = message.get_entities()
    photo, document, audio, video, voice = map(
        lambda x: x in message.raw_data,
        ("photo", "document", "audio", "video", "voice")
    )
    url, hashtag, email, bot_command = map(
        lambda x: any(e.type == x for e in entities),
        ("url", "hashtag", "email", "bot_command")
    )
    plain_text = message.get_plain_text()

    if photo:
        events.add(DispatcherEvent.PHOTO.value)

    if document:
        events.add(DispatcherEvent.FILE.value)

    if audio:
        events.add(DispatcherEvent.AUDIO.value)

    if video:
        events.add(DispatcherEvent.VIDEO.value)

    if voice:
        events.add(DispatcherEvent.VOICE.value)

    if url:
        events.add(DispatcherEvent.URL.value)

    if hashtag:
        events.add(DispatcherEvent.HASHTAG.value)

    if email:
        events.add(DispatcherEvent.EMAIL.value)

    if bot_command:
        events.add(DispatcherEvent.BOT_COMMAND.value)

    if plain_text:
        events.add(DispatcherEvent.PLAIN_TEXT.value)

    if not len(events):
        events.add(DispatcherEvent.NONE.value)

    return events


def match_events(a: Set[str], b: Set[str]) -> bool:
    """
    Checks if two groups of events are matched.

    :returns:
    `True` - match found, `False` otherwise.
    """
    return any(x in b for x in a)


def bind_command_to_date(
    user_id: int,
    chat_id: int,
    date: int,
    command: str
) -> None:
    """
    Binds command to date.

    You can use it to detect right command for messages
    with same date but without specific command.

    - stateful chat should be enabled.
    """
    key = f"dispatcher:date:{date}:command"
    expire = current_app.config[
        "RUNTIME_SAME_DATE_COMMAND_EXPIRE"
    ]

    set_user_chat_data(
        user_id,
        chat_id,
        key,
        command,
        expire
    )


def get_command_by_date(
    user_id: int,
    chat_id: int,
    date: int
) -> Union[str, None]:
    """
    - stateful chat should be enabled.

    :returns:
    Value that was set using `bind_command_to_date()`.
    """
    key = f"dispatcher:date:{date}:command"

    return get_user_chat_data(
        user_id,
        chat_id,
        key
    )
