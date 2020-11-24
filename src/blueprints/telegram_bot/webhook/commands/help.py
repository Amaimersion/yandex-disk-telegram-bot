from collections import deque

from flask import g, current_app

from src.api import telegram
from ._common.commands_content import (
    to_code,
    commands_html_content
)


def handle(*args, **kwargs):
    """
    Handles `/help` command.
    """
    chat_id = kwargs.get(
        "chat_id",
        g.telegram_chat.id
    )
    text = create_help_html_text()
    telegram.send_message(
        chat_id=chat_id,
        parse_mode="HTML",
        text=text,
        disable_web_page_preview=True
    )


def create_help_html_text() -> str:
    yd_upload_default_folder = current_app.config[
        "YANDEX_DISK_API_DEFAULT_UPLOAD_FOLDER"
    ]
    file_size_limit_in_mb = int(current_app.config[
        "TELEGRAM_API_MAX_FILE_SIZE"
    ] / 1024 / 1024)
    bullet_char = "•"
    text = deque()

    text.append(
        "You can interact with "
        '<a href="https://disk.yandex.com">Yandex.Disk</a> '
        "by using me. To control me send following commands."
        "\n\n"
        "Note:"
        "\n"
        f"{bullet_char} for uploading "
        f'"{to_code(yd_upload_default_folder)}" '
        "folder is used by default,"
        "\n"
        f"{bullet_char} maximum size of every upload "
        f"(except URL) is {file_size_limit_in_mb} MB."
        "\n"
    )

    for group in commands_html_content:
        group_name = group["name"]
        commands = group["commands"]
        group_added = False

        text.append(
            f"<b>{group_name}</b>"
        )

        for command in commands:
            command_name = command["name"]
            help_message = command.get("help")

            if help_message:
                text.append(
                    f"{bullet_char} {command_name} — {help_message}."
                )
                group_added = True

        if group_added:
            # extra line
            text.append("")
        else:
            # we don't want empty group name
            text.pop()

    return "\n".join(text)
