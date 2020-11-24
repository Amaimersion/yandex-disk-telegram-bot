from typing import (
    Union,
    Callable,
    Set
)
from collections import deque
import traceback

from src.extensions import redis_client
from src.blueprints.telegram_bot._common.stateful_chat import (
    get_disposable_handler,
    delete_disposable_handler,
    get_subscribed_handlers
)
from src.blueprints.telegram_bot._common.telegram_interface import (
    Message as TelegramMessage
)
from src.blueprints.telegram_bot._common.command_names import CommandName
from . import commands
from .dispatcher_events import (
    DispatcherEvent,
    RouteSource
)


def intellectual_dispatch(
    message: TelegramMessage
) -> Callable:
    """
    Intellectual dispatch to handlers of a message.
    Provides support for stateful chat (if Redis is enabled).

    Priority of handlers:
    1) if disposable handler exists and message events matches,
    then only that handler will be called and after removed
    2) if subscribed handlers exists, then only ones with events
    matched to message events will be called. If nothing is matched,
    then forwarding to № 3
    3) attempt to get first `bot_command` entity from message.
    If nothing found, then forwarding to № 4
    4) guessing of command that user assumed based on
    content of message

    Events matching:
    - if at least one event matched, then that handler will be
    marked as "matched".

    If stateful chat not enabled, then № 1 and № 2 will be skipped.

    Note: there can be multiple handlers picked for single message.
    Order of execution not determined.

    :param message:
    Incoming Telegram message.

    :returns:
    It is guaranteed that most appropriate callable handler that
    not raises an error will be returned. Function arguments already
    configured, but you can also provided your own through `*args`
    and `**kwargs`. You should call this function in order to run
    handlers (there can be multiple handlers in one return function).
    """
    user_id = message.get_user().id
    chat_id = message.get_chat().id
    stateful_chat_is_enabled = redis_client.is_enabled
    disposable_handler = None
    subscribed_handlers = None

    if stateful_chat_is_enabled:
        disposable_handler = get_disposable_handler(user_id, chat_id)
        subscribed_handlers = get_subscribed_handlers(user_id, chat_id)

    message_events = (
        detect_events(message) if (
            disposable_handler or
            subscribed_handlers
        ) else None
    )
    handler_names = deque()
    route_source = None

    if disposable_handler:
        match = match_events(
            message_events,
            disposable_handler["events"]
        )

        if match:
            route_source = RouteSource.DISPOSABLE_HANDLER
            handler_names.append(disposable_handler["name"])
            delete_disposable_handler(user_id, chat_id)

    if (
        subscribed_handlers and
        not handler_names
    ):
        for handler in subscribed_handlers:
            match = match_events(
                message_events,
                handler["events"]
            )

            if match:
                route_source = RouteSource.SUBSCRIBED_HANDLER
                handler_names.append(handler["name"])

    if not handler_names:
        command = message.get_entity_value("bot_command")

        if command:
            route_source = RouteSource.DIRECT_COMMAND
            handler_names.append(command)

    if not handler_names:
        route_source = RouteSource.GUESSED_COMMAND
        handler_names.append(guess_bot_command(message))

    def method(*args, **kwargs):
        for handler_name in handler_names:
            handler_method = direct_dispatch(handler_name)

            try:
                handler_method(
                    *args,
                    **kwargs,
                    user_id=user_id,
                    chat_id=chat_id,
                    message=message,
                    route_source=route_source,
                    message_events=message_events
                )
            except Exception as error:
                print(
                    f"{handler_name}: {error}",
                    "\n",
                    traceback.format_exc()
                )

    return method


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
    Fallback handler that will be used in case
    if command is unknown.

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
        CommandName.SPACE.value: commands.space_handler,
        CommandName.ELEMENT_INFO.value: commands.element_info_handler,
        CommandName.DISK_INFO.value: commands.disk_info_handler
    }
    handler = routes.get(command, fallback)

    def method(*args, **kwargs):
        handler(*args, **kwargs)

    return method


def guess_bot_command(
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


def detect_events(
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


def match_events(
    a: Set[str],
    b: Set[str]
) -> bool:
    """
    Checks if two groups of events are matched.

    :returns:
    `True` - match found, `False` otherwise.
    """
    return any(x in b for x in a)
