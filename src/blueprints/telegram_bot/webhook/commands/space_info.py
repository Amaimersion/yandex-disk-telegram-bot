from string import ascii_letters, digits, Template
from datetime import datetime, timezone

from flask import g, current_app

from src.rq import task_queue, prepare_task, run_task
from src.http import telegram
from src.i18n import gettext
from src.blueprints._common.utils import get_current_iso_datetime
from src.blueprints.telegram_bot._common.yandex_disk import (
    get_disk_info,
    YandexAPIRequestError
)
from src.blueprints.telegram_bot._common.command_names import (
    CommandName
)
from ._common.responses import cancel_command
from ._common.decorators import (
    yd_access_token_required
)


# `plotly` uses too much RAM.
# Disabled at the moment, will be refactored in future
USE_GRAPH = False


if USE_GRAPH:
    from plotly.graph_objects import Pie, Figure
    from plotly.express import colors
    from plotly.io import to_image


@yd_access_token_required
def handle(*args, **kwargs):
    """
    Handles `/space_info` command.
    """
    if USE_GRAPH:
        handle_with_graph(*args, **kwargs)
    else:
        handle_with_text(*args, **kwargs)


def handle_with_text(*args, **kwargs):
    """
    Handles `/space_info` command using plain text.
    """
    user = g.db_user
    chat_id = kwargs.get(
        "chat_id",
        g.telegram_chat.id
    )
    access_token = user.yandex_disk_token.get_access_token()
    disk_info = None

    try:
        disk_info = get_disk_info(access_token)
    except YandexAPIRequestError as error:
        cancel_command(
            chat_telegram_id=chat_id
        )

        raise error

    total_space = disk_info.get("total_space", 0)
    used_space = disk_info.get("used_space", 0)
    trash_size = disk_info.get("trash_size", 0)

    free_space_in_gb = b_to_gb(total_space - used_space - trash_size)
    total_space_in_gb = b_to_gb(total_space)
    used_space_in_gb = b_to_gb(used_space)
    trash_size_in_gb = b_to_gb(trash_size)
    free_space_in_p = to_percent(total_space_in_gb, free_space_in_gb)
    used_space_in_p = to_percent(total_space_in_gb, used_space_in_gb)
    trash_size_in_p = to_percent(total_space_in_gb, trash_size_in_gb)

    current_utc_date = get_current_utc_datetime()
    title = gettext(
        "Yandex.Disk space at %(current_utc_date)s",
        current_utc_date=current_utc_date
    )
    gb_text = gettext("GB")
    total_text = gettext("Total")
    used_text = gettext("Used")
    free_text = gettext("Free")
    trash_text = gettext("Trash")

    space_template = Template("<b>$name:</b> $size $unit, $percent%")

    message = (
        title +
        "\n\n" +
        space_template.substitute(
            name=total_text,
            size=f"{total_space_in_gb:.2f}",
            unit=gb_text,
            percent=100
        ) +
        "\n" +
        space_template.substitute(
            name=free_text,
            size=f"{free_space_in_gb:.2f}",
            unit=gb_text,
            percent=f"{free_space_in_p:.0f}"
        ) +
        "\n" +
        space_template.substitute(
            name=used_text,
            size=f"{used_space_in_gb:.2f}",
            unit=gb_text,
            percent=f"{used_space_in_p:.0f}"
        ) +
        "\n" +
        space_template.substitute(
            name=trash_text,
            size=f"{trash_size_in_gb:.2f}",
            unit=gb_text,
            percent=f"{trash_size_in_p:.0f}"
        )
    )

    telegram.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="HTML"
    )


def handle_with_graph(*args, **kwargs):
    """
    Handles `/space_info` command using graphs.
    """
    user = g.db_user
    chat_id = kwargs.get(
        "chat_id",
        g.telegram_chat.id
    )
    access_token = user.yandex_disk_token.get_access_token()
    disk_info = None

    # If all task queue workers are busy,
    # it can take a long time before they
    # execute `send_photo()` function.
    # We will indicate to user that everything
    # is fine and result will be sent soon
    sended_message = telegram.send_message(
        chat_id=chat_id,
        text=gettext("Generating...")
    )
    sended_message_id = sended_message["content"]["message_id"]

    try:
        disk_info = get_disk_info(access_token)
    except YandexAPIRequestError as error:
        cancel_command(
            chat_telegram_id=chat_id,
            edit_message=sended_message_id
        )

        raise error

    current_utc_date = get_current_utc_datetime()
    current_iso_date = get_current_iso_datetime()
    jpeg_image = create_space_chart(
        total_space=disk_info["total_space"],
        used_space=disk_info["used_space"],
        trash_size=disk_info["trash_size"],
        caption=current_utc_date
    )
    filename = f"{to_filename(current_iso_date)}.jpg"
    file_caption = gettext(
        "Yandex.Disk space at %(current_utc_date)s",
        current_utc_date=current_utc_date
    )
    arguments = (
        jpeg_image,
        filename,
        file_caption,
        chat_id,
        sended_message_id
    )

    if task_queue.is_enabled:
        job_timeout = current_app.config[
            "RUNTIME_SPACE_INFO_WORKER_TIMEOUT"
        ]
        prepare_data = prepare_task()

        task_queue.enqueue(
            run_task,
            kwargs={
                "f": send_photo,
                "args": arguments,
                "prepare_data": prepare_data
            },
            description=CommandName.SPACE_INFO.value,
            job_timeout=job_timeout,
            result_ttl=0,
            failure_ttl=0
        )
    else:
        send_photo(*arguments)


def create_space_chart(
    total_space: int,
    used_space: int,
    trash_size: int,
    caption: str = None
) -> bytes:
    """
    Creates Yandex.Disk space chart.

    - all sizes (total, used, trash) should be
    specified in binary bytes. They will be
    converted to binary gigabytes.

    :returns: JPEG image as bytes.
    """
    free_space = b_to_gb(total_space - used_space - trash_size)
    total_space = b_to_gb(total_space)
    used_space = b_to_gb(used_space)
    trash_size = b_to_gb(trash_size)
    gb_text = gettext("GB")
    total_text = gettext("Total")
    chart = Pie(
        labels=[
            gettext("Used Space"),
            gettext("Free Space"),
            gettext("Trash Size")
        ],
        values=[
            used_space,
            free_space,
            trash_size
        ],
        text=[
            gettext("Used"),
            gettext("Free"),
            gettext("Trash")
        ],
        marker={
            "colors": [
                colors.sequential.Rainbow[3],
                colors.sequential.Rainbow[5],
                colors.sequential.Rainbow[8]
            ],
            "line": {
                "width": 0.2
            }
        },
        sort=False,
        direction="clockwise",
        texttemplate=(
            "%{text}<br />"
            "<b>%{value:.2f} "
            f"{gb_text}</b><br />"
            "%{percent}"
        ),
        textposition="outside",
        hole=0.5
    )
    figure = Figure(
        data=chart,
        layout={
            "title": {
                "text": caption,
                "font": {
                    "size": 20
                }
            },
            "annotations": [
                {
                    "align": "center",
                    "showarrow": False,
                    "text": (
                        f"{total_text}<br />"
                        f"<b>{total_space:.2f} {gb_text}</b><br />"
                        "100%"
                    )
                }
            ],
            "width": 1000,
            "height": 800,
            "font": {
                "size": 27
            },
            "margin": {
                "t": 140,
                "b": 40,
                "r": 230,
                "l": 165
            }
        }
    )

    return to_image(figure, format="jpeg")


def b_to_gb(value: int) -> int:
    """
    Converts binary bytes to binary gigabytes.
    """
    return (value / 1024 / 1024 / 1024)


def to_percent(whole: int, part: int) -> int:
    """
    :returns: `part` as percentage of `whole`.
    """
    return (part * 100 / whole)


def get_current_utc_datetime() -> str:
    """
    :returns: Current date as string representation.
    """
    now = datetime.now(timezone.utc)

    return now.strftime("%d.%m.%Y %H:%M %Z")


def to_filename(value: str) -> str:
    """
    :returns: Valid filename.
    """
    valid_chars = f"-_.{ascii_letters}{digits}"
    filename = value.lower()
    filename = (
        filename
        .replace(" ", "_")
        .replace(":", "_")
    )
    filename = "".join(x for x in filename if x in valid_chars)

    return filename


def send_photo(
    content: bytes,
    filename: str,
    file_caption: str,
    chat_id: int,
    sended_message_id: int
):
    """
    Sends photo to user.
    """
    telegram.send_photo(
        chat_id=chat_id,
        photo=(
            filename,
            content,
            "image/jpeg"
        ),
        caption=file_caption
    )

    try:
        telegram.delete_message(
            chat_id=chat_id,
            message_id=sended_message_id
        )
    except Exception:
        # we can safely ignore if we can't delete
        # sended message. Anyway we will send new one
        pass
