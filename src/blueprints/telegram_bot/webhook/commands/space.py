from string import ascii_letters, digits
from datetime import datetime, timezone

from flask import g
from plotly.graph_objects import Pie, Figure
from plotly.express import colors
from plotly.io import to_image

from src.api import telegram
from .common.responses import (
    cancel_command,
    AbortReason
)
from .common.decorators import (
    yd_access_token_required,
    get_db_data
)
from .common.yandex_api import (
    get_disk_info,
    YandexAPIRequestError
)
from . import CommandName


@yd_access_token_required
@get_db_data
def handle(*args, **kwargs):
    """
    Handles `/publish` command.
    """
    user = g.db_user
    chat = g.db_chat
    access_token = user.yandex_disk_token.get_access_token()
    disk_info = None

    try:
        disk_info = get_disk_info(access_token)
    except YandexAPIRequestError as error:
        print(error)
        return cancel_command(chat.telegram_id)

    current_date = get_current_date()
    jpeg_image = create_space_chart(
        total_space=disk_info["total_space"],
        used_space=disk_info["used_space"],
        trash_size=disk_info["trash_size"],
        caption=current_date
    )

    telegram.send_photo(
        chat_id=chat.telegram_id,
        photo=(
            f"{to_filename(current_date)}.jpg",
            jpeg_image,
            "image/jpeg"
        ),
        caption=f"Yandex.Disk space at {current_date}"
    )


def create_space_chart(
    total_space: int,
    used_space: int,
    trash_size: int,
    caption: str = None
) -> bytes:
    """
    Creates Yandex.Disk space chart.

    - all sizes (total, used, trash) should be
    specified in binary bytes (B). They will be
    converted to binary gigabytes (GB).

    :returns: JPEG image as bytes.
    """
    free_space = b_to_gb(total_space - used_space - trash_size)
    total_space = b_to_gb(total_space)
    used_space = b_to_gb(used_space)
    trash_size = b_to_gb(trash_size)

    chart = Pie(
        labels=[
            "Used Space",
            "Trash Size",
            "Free Space"
        ],
        values=[
            used_space,
            trash_size,
            free_space
        ],
        text=[
            "Used",
            "Trash",
            "Free"
        ],
        marker={
            "colors": [
                colors.sequential.Rainbow[3],
                colors.sequential.Rainbow[8],
                colors.sequential.Rainbow[5]
            ],
            "line": {
                "width": 0.2
            }
        },
        sort=False,
        direction="clockwise",
        texttemplate=(
            "%{text}<br />"
            "<b>%{value:.2f} GB</b><br />"
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
                        "Total<br />"
                        f"<b>{total_space:.2f} GB</b><br />"
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


def get_current_date() -> str:
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
