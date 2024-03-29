from typing import Union
from collections import deque
import json

from src.i18n import gettext
from src.blueprints._common.utils import (
    convert_iso_datetime,
    bytes_to_human_decimal
)
from src.blueprints.telegram_bot._common.telegram_interface import (
    Message as TelegramMessage
)
from src.blueprints.telegram_bot.webhook.dispatcher_interface import (
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
            gettext(
                "<b>Name:</b> %(name)s",
                name=info["name"]
            )
        )

    if "type" in info:
        incoming_type = info["type"].lower()
        value = gettext("Unknown")

        if (incoming_type == "dir"):
            value = gettext("Folder")
        elif (incoming_type == "file"):
            if "media_type" in info:
                value = info["media_type"]
            else:
                value = gettext("File")

            if "mime_type" in info:
                value = f"{value} ({info['mime_type']})"

        text.append(
            gettext(
                "<b>Type:</b> %(type)s",
                type=value
            )
        )

    if "size" in info:
        bytes_count = info["size"]
        bytes_text = gettext("bytes")
        value = f"{bytes_count:,} {bytes_text}"

        if (bytes_count >= 1000):
            decimal = bytes_to_human_decimal(bytes_count)
            value = f"{decimal} ({bytes_count:,} {bytes_text})"

        text.append(
            gettext(
                "<b>Size:</b> %(size)s",
                size=value
            )
        )

    if (
        include_private_info and
        ("created" in info)
    ):
        value = convert_iso_datetime(info["created"])
        text.append(
            gettext(
                "<b>Created:</b> "
                "%(date)s %(time)s %(timezone)s",
                date=value['date'],
                time=value['time'],
                timezone=value['timezone']
            )
        )

    if (
        include_private_info and
        ("modified" in info)
    ):
        value = convert_iso_datetime(info["modified"])
        text.append(
            gettext(
                "<b>Modified:</b> "
                "%(date)s %(time)s %(timezone)s",
                date=value['date'],
                time=value['time'],
                timezone=value['timezone']
            )
        )

    if (
        include_private_info and
        ("path" in info)
    ):
        text.append(
            gettext(
                "<b>Full path:</b> "
                "<code>%(path)s</code>",
                path=info["path"]
            )
        )

    if (
        include_private_info and
        ("origin_path" in info)
    ):
        text.append(
            gettext(
                "<b>Origin path:</b> "
                "<code>%(path)s</code>",
                path=info["origin_path"]
            )
        )

    if (
        ("_embedded" in info) and
        ("total" in info["_embedded"])
    ):
        text.append(
            gettext(
                "<b>Total elements:</b> %(count)s",
                count=info["_embedded"]["total"]
            )
        )

    if "public_url" in info:
        text.append(
            gettext(
                "<b>Public URL:</b> %(url)s",
                url=info["public_url"]
            )
        )

    if (
        include_private_info and
        ("views_count" in info)
    ):
        text.append(
            gettext(
                "<b>Views:</b> %(count)s",
                count=info["views_count"]
            )
        )

    if (
        include_private_info and
        ("owner" in info)
    ):
        data = info["owner"]
        name = data.get("display_name")
        login = data.get("login")
        value = "?"

        if name:
            value = name

        if (
            value and
            login and
            (value != login)
        ):
            value = f"{value} ({login})"
        elif login:
            value = login

        text.append(
            gettext(
                "<b>Owner:</b> %(owner)s",
                owner=value
            )
        )

    if (
        include_private_info and
        ("share" in info)
    ):
        data = info["share"]

        if "is_owned" in data:
            value = gettext("No")

            if data["is_owned"]:
                value = gettext("Yes")

            text.append(
                gettext(
                    "<b>Shared access — Owner:</b> %(status)s",
                    status=value
                )
            )

        if "rights" in data:
            value = data["rights"].lower()

            if (value == "rw"):
                value = gettext("Full access")
            elif (value == "r"):
                value = gettext("Read")
            elif (value == "w"):
                value = gettext("Write")

            text.append(
                gettext(
                    "<b>Shared access — Rights:</b> %(rights)s",
                    rights=value
                )
            )

        if "is_root" in data:
            value = gettext("No")

            if data["is_root"]:
                value = gettext("Yes")

            text.append(
                gettext(
                    "<b>Shared access — Root:</b> %(status)s",
                    status=value
                )
            )

    if (
        include_private_info and
        ("exif" in info) and
        info["exif"]
    ):
        exif = json.dumps(info["exif"], indent=4)
        text.append(
            gettext(
                "<b>EXIF:</b> "
                "<code>%(exif)s</code>",
                exif=exif
            )
        )

    if "sha256" in info:
        text.append(
            gettext(
                "<b>SHA-256:</b> %(value)s",
                value=info["sha256"]
            )
        )

    if "md5" in info:
        text.append(
            gettext(
                "<b>MD5:</b> %(value)s",
                value=info["md5"]
            )
        )

    return "\n".join(text)
