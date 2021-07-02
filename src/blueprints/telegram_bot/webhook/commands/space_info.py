from string import ascii_letters, digits
from datetime import datetime, timezone

from flask import g, current_app
from plotly.graph_objects import Pie, Figure
from plotly.express import colors
from plotly.io import to_image

from src.rq import task_queue, prepare_task, run_task
from src.api import telegram
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


@yd_access_token_required
def handle(*args, **kwargs):
    """
    Handles `/space_info` command.
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
