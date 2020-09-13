from flask import (
    request,
    g,
    make_response
)

from src.blueprints.telegram_bot import telegram_bot_blueprint as bp
from . import commands, telegram_interface


@bp.route("/webhook", methods=["POST"])
def webhook():
    """
    Handles Webhook POST request from Telegram server.

    - for Webhook we always should return 200 to indicate
    that we successfully got an update, otherwise Telegram
    will flood the server. So, not use `abort()` or anything.
    """
    raw_data = request.get_json(
        force=True,
        silent=True,
        cache=False
    )

    if (raw_data is None):
        return make_error_response()

    telegram_request = telegram_interface.Request(raw_data)

    if not (telegram_request.is_valid()):
        return make_error_response()

    message = telegram_request.get_message()

    if not (message.is_valid()):
        return make_error_response()

    g.telegram_message = message
    g.telegram_user = message.get_user()
    g.telegram_chat = message.get_chat()
    g.route_to = route_command

    command = message.get_entity_value("bot_command")

    if (command is None):
        command = message.guess_bot_command()

    route_command(command)

    return make_success_response()


def route_command(command: str) -> None:
    """
    Routes command to specific handler.
    """
    CommandNames = commands.CommandsNames

    if (isinstance(command, CommandNames)):
        command = command.value

    routes = {
        CommandNames.START.value: commands.help_handler,
        CommandNames.HELP.value: commands.help_handler,
        CommandNames.ABOUT.value: commands.about_handler,
        CommandNames.SETTINGS.value: commands.settings_handler,
        CommandNames.YD_AUTH.value: commands.yd_auth_handler,
        CommandNames.YD_REVOKE.value: commands.yd_revoke_handler,
        CommandNames.UPLOAD_PHOTO.value: commands.upload_photo_handler,
        CommandNames.UPLOAD_FILE.value: commands.upload_file_handler,
        CommandNames.UPLOAD_AUDIO.value: commands.upload_audio_handler,
        CommandNames.UPLOAD_VIDEO.value: commands.upload_video_handler,
        CommandNames.UPLOAD_VOICE.value: commands.upload_voice_handler,
        CommandNames.UPLOAD_URL.value: commands.upload_url_handler,
        CommandNames.CREATE_FOLDER.value: commands.create_folder_handler,
        CommandNames.PUBLISH.value: commands.publish_handler,
        CommandNames.UNPUBLISH.value: commands.unpublish_handler,
        CommandNames.SPACE.value: commands.space_handler
    }
    method = routes.get(command, commands.unknown_handler)

    method()


def make_error_response():
    """
    Creates error response for Telegram Webhook.
    """
    return make_response((
        {
            "ok": False,
            "error_code": 400
        },
        200
    ))


def make_success_response():
    """
    Creates success response for Telegram Webhook.
    """
    return make_response((
        {
            "ok": True
        },
        200
    ))
