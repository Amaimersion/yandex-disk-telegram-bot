from collections import deque

from flask import g, current_app

from src.api import telegram
from src.i18n import gettext
from src.blueprints.telegram_bot._common.command_names import (
    CommandName
)
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
    file_size_limit_in_mb = int(current_app.config[
        "TELEGRAM_API_MAX_FILE_SIZE"
    ] / 1024 / 1024)
    bullet_char = gettext("•")
    message = gettext(
        "You can interact with "
        '<a href="https://disk.yandex.com">Yandex.Disk</a> '
        "by using me. To control me send following commands."
        "\n\n"
        "Note:"
        "\n"
        "%(bullet_char)s you can change default upload folder "
        "using %(settings_command)s command,"
        "\n"
        "%(bullet_char)s maximum size of every upload "
        "(except URL) is %(file_size_limit_in_mb)s MB."
        "\n",
        bullet_char=bullet_char,
        settings_command=CommandName.SETTINGS.value,
        file_size_limit_in_mb=file_size_limit_in_mb
    )
    text = deque()

    text.append(message)

    for group in commands_html_content:
        group_name = group["name"]
        commands = group["commands"]
        group_added = False

        text.append(
            gettext(
                "<b>%(group_name)s</b>",
                group_name=group_name
            )
        )

        for command in commands:
            command_name = command["name"]
            help_message = command.get("help")

            if help_message:
                message = gettext(
                    "%(bullet_char)s %(command_name)s — %(help_message)s.",
                    bullet_char=bullet_char,
                    command_name=command_name,
                    help_message=help_message
                )
                text.append(message)
                group_added = True

        if group_added:
            # extra line
            text.append("")
        else:
            # we don't want empty group name
            text.pop()

    return "\n".join(text)
