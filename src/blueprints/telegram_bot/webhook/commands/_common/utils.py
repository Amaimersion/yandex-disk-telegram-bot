from typing import Union

from src.blueprints.telegram_bot._common.telegram_interface import (
    Message as TelegramMessage
)
from src.blueprints.telegram_bot.webhook.dispatcher_events import (
    RouteSource
)


def extract_absolute_path(
    message: TelegramMessage,
    bot_command: str,
    route_source: Union[RouteSource, None],
) -> str:
    """
    Extracts absolute path from Telegram message.
    It supports both: folders and files.

    :param message:
    Incoming Telegram message.
    :param bot_command:
    Bot command which will be removed from message.
    :param route_source:
    It is dispatcher parameter, see it documentation.
    You should always pass it, even if it is `None`.
    Bot command will be deleted from start of a message
    when it is equal to `DISPOSABLE_HANDLER`.

    :returns:
    Extracted absolute path. Can be empty.
    """
    path = message.get_text()

    # On "Disposable handler" route we expect pure text,
    # in other cases we expect bot command as start of a message
    if (route_source != RouteSource.DISPOSABLE_HANDLER):
        path = path.replace(
            bot_command,
            "",
            1
        ).strip()

    return path
