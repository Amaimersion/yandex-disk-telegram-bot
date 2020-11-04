from typing import Union, Callable

from . import commands
from .commands import CommandsNames
from .telegram_interface import (
    Message as TelegramMessage
)


def dispatch(message: TelegramMessage) -> Callable:
    """
    Dispatch to handler of a message.
    It handles message by different ways: tries to
    read the content, tries to guess the command,
    tries to implement stateful dialog, tries to pass
    most appropriate arguments, and so on.
    So, most appropriate handler will be returned
    for incoming message.

    :param message:
    Incoming Telegram message.

    :returns:
    It is guaranteed that most appropriate callable
    handler will be returned. It is a handler for
    incoming message with already configured arguments,
    and you should call this with no arguments
    (but you can pass any if you want).
    """
    command = message.get_entity_value("bot_command")

    if command is None:
        command = guess_bot_command(message)

    handler = direct_dispatch(command)

    def method(*args, **kwargs):
        handler(*args, **kwargs)

    return method


def direct_dispatch(
    command: Union[CommandsNames, str],
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
    if isinstance(command, CommandsNames):
        command = command.value

    routes = {
        CommandsNames.START.value: commands.help_handler,
        CommandsNames.HELP.value: commands.help_handler,
        CommandsNames.ABOUT.value: commands.about_handler,
        CommandsNames.SETTINGS.value: commands.settings_handler,
        CommandsNames.YD_AUTH.value: commands.yd_auth_handler,
        CommandsNames.YD_REVOKE.value: commands.yd_revoke_handler,
        CommandsNames.UPLOAD_PHOTO.value: commands.upload_photo_handler,
        CommandsNames.UPLOAD_FILE.value: commands.upload_file_handler,
        CommandsNames.UPLOAD_AUDIO.value: commands.upload_audio_handler,
        CommandsNames.UPLOAD_VIDEO.value: commands.upload_video_handler,
        CommandsNames.UPLOAD_VOICE.value: commands.upload_voice_handler,
        CommandsNames.UPLOAD_URL.value: commands.upload_url_handler,
        CommandsNames.CREATE_FOLDER.value: commands.create_folder_handler,
        CommandsNames.PUBLISH.value: commands.publish_handler,
        CommandsNames.UNPUBLISH.value: commands.unpublish_handler,
        CommandsNames.SPACE.value: commands.space_handler
    }
    handler = routes.get(command, fallback)

    def method(*args, **kwargs):
        handler(*args, **kwargs)

    return method


def guess_bot_command(
    message: TelegramMessage,
    fallback: CommandsNames = CommandsNames.HELP
) -> CommandsNames:
    """
    Tries to guess which bot command user
    assumed based on content of a message.

    :param fallback:
    Fallback command which will be returned if unable to guess.

    :returns:
    Guessed bot command based on a message.
    """
    command = fallback
    raw_data = message.raw_data

    if ("photo" in raw_data):
        command = CommandsNames.UPLOAD_PHOTO
    elif ("document" in raw_data):
        command = CommandsNames.UPLOAD_FILE
    elif ("audio" in raw_data):
        command = CommandsNames.UPLOAD_AUDIO
    elif ("video" in raw_data):
        command = CommandsNames.UPLOAD_VIDEO
    elif ("voice" in raw_data):
        command = CommandsNames.UPLOAD_VOICE
    elif (message.get_entity_value("url") is not None):
        command = CommandsNames.UPLOAD_URL

    return command
