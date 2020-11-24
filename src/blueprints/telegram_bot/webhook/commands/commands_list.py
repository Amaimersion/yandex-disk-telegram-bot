from collections import deque

from flask import g

from src.api import telegram
from src.blueprints.telegram_bot._common.command_names import CommandName


def handle(*args, **kwargs):
    """
    Handles `/commands` command.
    """
    chat_id = kwargs.get(
        "chat_id",
        g.telegram_chat.id
    )
    text = create_commands_list_html_text()

    telegram.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML"
    )


def create_commands_list_html_text() -> str:
    content = (
        {
            "name": "Yandex.Disk",
            "commands": (
                {
                    "name": CommandName.UPLOAD_PHOTO.value
                },
                {
                    "name": CommandName.PUBLIC_UPLOAD_PHOTO.value
                },
                {
                    "name": CommandName.UPLOAD_FILE.value
                },
                {
                    "name": CommandName.PUBLIC_UPLOAD_FILE.value
                },
                {
                    "name": CommandName.UPLOAD_AUDIO.value
                },
                {
                    "name": CommandName.PUBLIC_UPLOAD_AUDIO.value
                },
                {
                    "name": CommandName.UPLOAD_VIDEO.value
                },
                {
                    "name": CommandName.PUBLIC_UPLOAD_VIDEO.value
                },
                {
                    "name": CommandName.UPLOAD_VOICE.value
                },
                {
                    "name": CommandName.PUBLIC_UPLOAD_VOICE.value
                },
                {
                    "name": CommandName.UPLOAD_URL.value
                },
                {
                    "name": CommandName.PUBLIC_UPLOAD_URL.value
                },
                {
                    "name": CommandName.PUBLISH.value
                },
                {
                    "name": CommandName.UNPUBLISH.value
                },
                {
                    "name": CommandName.CREATE_FOLDER.value
                },
                {
                    "name": CommandName.ELEMENT_INFO.value
                },
                {
                    "name": CommandName.SPACE_INFO.value
                },
                {
                    "name": CommandName.DISK_INFO.value
                }
            )
        },
        {
            "name": "Yandex.Disk Access",
            "commands": (
                {
                    "name": CommandName.YD_AUTH.value
                },
                {
                    "name": CommandName.YD_REVOKE.value
                }
            )
        },
        {
            "name": "Settings",
            "commands": (
                {
                    "name": CommandName.SETTINGS.value
                },
            )
        },
        {
            "name": "Information",
            "commands": (
                {
                    "name": CommandName.ABOUT.value
                },
                {
                    "name": CommandName.COMMANDS_LIST.value
                }
            )
        }
    )
    text = deque()

    for group in content:
        text.append(
            f"<b>{group['name']}</b>"
        )

        for command in group["commands"]:
            text.append(command["name"])

        text.append("")

    return "\n".join(text)
