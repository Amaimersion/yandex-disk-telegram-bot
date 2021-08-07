from collections import deque

from flask import g, current_app

from src.http import telegram
from src.i18n import gettext
from src.blueprints._common.utils import bytes_to_human_binary
from src.blueprints.telegram_bot._common.yandex_disk import (
    get_disk_info,
    YandexAPIRequestError
)
from ._common.responses import cancel_command
from ._common.decorators import (
    yd_access_token_required
)


@yd_access_token_required
def handle(*args, **kwargs):
    """
    Handles `/disk_info` command.
    """
    chat_id = kwargs.get(
        "chat_id",
        g.telegram_chat.id
    )
    user = g.db_user
    access_token = user.yandex_disk_token.get_access_token()
    info = None

    try:
        info = get_disk_info(access_token)
    except YandexAPIRequestError as error:
        cancel_command(chat_id)
        raise error

    text = create_disk_info_html_text(info)

    telegram.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


def create_disk_info_html_text(info: dict) -> str:
    """
    :param info:
    https://dev.yandex.net/disk-polygon/?lang=ru&tld=ru#!/v147disk/GetDisk
    """
    text = deque()

    if "user" in info:
        data = info["user"]

        if "display_name" in data:
            text.append(
                gettext(
                    "<b>User — Name:</b> %(display_name)s",
                    display_name=data["display_name"]
                )
            )

        if "login" in data:
            text.append(
                gettext(
                    "<b>User — Login:</b> %(login)s",
                    login=data["login"]
                )
            )

        if "country" in data:
            text.append(
                gettext(
                    "<b>User — Country:</b> %(country)s",
                    country=data["country"]
                )
            )

    if "is_paid" in info:
        value = gettext("?")

        if info["is_paid"]:
            value = gettext("Yes")
        else:
            value = gettext("No")

        text.append(
            gettext(
                "<b>Paid:</b> %(status)s",
                status=value
            )
        )

    if "total_space" in info:
        value = bytes_to_string(info["total_space"])

        text.append(
            gettext(
                "<b>Total space:</b> %(value)s",
                value=value
            )
        )

    if "used_space" in info:
        value = bytes_to_string(info["used_space"])

        text.append(
            gettext(
                "<b>Used space:</b> %(value)s",
                value=value
            )
        )

    if (
        ("total_space" in info) and
        ("used_space" in info) and
        ("trash_size" in info)
    ):
        bytes_count = (
            info["total_space"] -
            info["used_space"] -
            info["trash_size"]
        )
        value = bytes_to_string(bytes_count)

        text.append(
            gettext(
                "<b>Free space:</b> %(value)s",
                value=value
            )
        )

    if "trash_size" in info:
        value = bytes_to_string(info["trash_size"])

        text.append(
            gettext(
                "<b>Trash size:</b> %(value)s",
                value=value
            )
        )

    if "max_file_size" in info:
        value = bytes_to_string(info["max_file_size"])

        text.append(
            gettext(
                "<b>Maximum file size:</b> %(value)s",
                value=value
            )
        )

    return "\n".join(text)


def bytes_to_string(bytes_count: int) -> str:
    bytes_word = gettext("bytes")
    value = f"{bytes_count:,} {bytes_word}"

    if (bytes_count >= 1000):
        decimal = bytes_to_human_binary(bytes_count)
        value = f"{decimal} ({bytes_count:,} {bytes_word})"

    return value
