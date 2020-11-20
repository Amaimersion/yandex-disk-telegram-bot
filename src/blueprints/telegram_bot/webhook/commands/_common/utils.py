from typing import Union
from collections import deque
import json

from src.blueprints._common.utils import (
    convert_iso_datetime,
    bytes_to_human_decimal
)
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


def create_element_info_html_text(
    info: dict,
    include_private_info: bool
) -> str:
    """
    :param info:
    - https://yandex.ru/dev/disk/api/reference/meta.html/
    - https://dev.yandex.net/disk-polygon/?lang=ru&tld=ru#!/v147disk47resources/GetResource # noqa
    :param include_private_info:
    Include private information in result.
    "Private information" means information that
    can compromise a user (for example, full path of element).
    Use `True` when you want to display this text only to user,
    use `False` when you can assume that user theoretically can
    forward this text to some another user(s).
    """
    text = deque()

    if "name" in info:
        text.append(
            f"<b>Name</b>: {info['name']}"
        )

    if "type" in info:
        incoming_type = info["type"].lower()
        value = "Unknown"

        if (incoming_type == "dir"):
            value = "Folder"
        elif (incoming_type == "file"):
            if "media_type" in info:
                value = info["media_type"]
            else:
                value = "File"

            if "mime_type" in info:
                value = f"{value} ({info['mime_type']})"

        text.append(
            f"<b>Type</b>: {value}"
        )

    if "size" in info:
        bytes_count = info["size"]
        value = f"{bytes_count:,} bytes"

        if (bytes_count >= 1000):
            decimal = bytes_to_human_decimal(bytes_count)
            value = f"{decimal} ({bytes_count:,} bytes)"

        text.append(
            f"<b>Size</b>: {value}"
        )

    if (
        include_private_info and
        ("created" in info)
    ):
        value = convert_iso_datetime(info["created"])
        text.append(
            "<b>Created</b>: "
            f"{value['date']} {value['time']} {value['timezone']}"
        )

    if (
        include_private_info and
        ("modified" in info)
    ):
        value = convert_iso_datetime(info["modified"])
        text.append(
            "<b>Modified</b>: "
            f"{value['date']} {value['time']} {value['timezone']}"
        )

    if (
        include_private_info and
        ("path" in info)
    ):
        text.append(
            "<b>Full path</b>: "
            f"<code>{info['path']}</code>"
        )

    if (
        include_private_info and
        ("origin_path" in info)
    ):
        text.append(
            "<b>Origin path</b>: "
            f"<code>{info['origin_path']}</code>"
        )

    if (
        ("_embedded" in info) and
        ("total" in info["_embedded"])
    ):
        text.append(
            f"<b>Total elements</b>: {info['_embedded']['total']}"
        )

    if "public_url" in info:
        text.append(
            f"<b>Public URL</b>: {info['public_url']}"
        )

    if "sha256" in info:
        text.append(
            f"<b>SHA-256</b>: {info['sha256']}"
        )

    if "md5" in info:
        text.append(
            f"<b>MD5</b>: {info['md5']}"
        )

    if (
        include_private_info and
        ("share" in info)
    ):
        data = info["share"]

        if "is_owned" in data:
            value = "No"

            if data["is_owned"]:
                value = "Yes"

            text.append(
                f"<b>Shared access — Owner</b>: {value}"
            )

        if "rights" in data:
            value = data["rights"].lower()

            if (value == "rw"):
                value = "Full access"
            elif (value == "r"):
                value = "Read"
            elif (value == "w"):
                value = "Write"

            text.append(
                f"<b>Shared access — Rights</b>: {value}"
            )

        if "is_root" in data:
            value = "No"

            if data["is_root"]:
                value = "Yes"

            text.append(
                f"<b>Shared access — Root</b>: {value}"
            )

    if (
        include_private_info and
        ("exif" in info) and
        info["exif"]
    ):
        exif = json.dumps(info["exif"], indent=4)
        text.append(
            "<b>EXIF</b>: "
            f"<code>{exif}</code>"
        )

    return "\n".join(text)
