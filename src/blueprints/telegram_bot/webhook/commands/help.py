# flake8: noqa

from flask import g, current_app

from src.api import telegram
from . import CommandsNames


def handle():
    """
    Handles `/help` command.
    """
    yd_upload_default_folder = current_app.config[
        "YANDEX_DISK_API_DEFAULT_UPLOAD_FOLDER"
    ]
    file_size_limit_in_mb = int(current_app.config[
        "TELEGRAM_API_MAX_FILE_SIZE"
    ] / 1000 / 1000)

    text = (
        "You can control me by sending these commands:"
        "\n\n"
        "<b>Yandex.Disk</b>"
        "\n"
        f'For uploading "{to_code(yd_upload_default_folder)}" folder is used by default.'
        "\n"
        f'Maximum size of every upload (except URL) is {file_size_limit_in_mb} MB.'
        "\n"
        f"{CommandsNames.UPLOAD_PHOTO.value} — upload a photo. "
        "Original name will be not saved, quality of photo will be decreased. "
        "You can send photo without this command."
        "\n"
        f"{CommandsNames.UPLOAD_FILE.value} — upload a file. "
        "Original name will be saved. "
        "For photos, original quality will be saved. "
        "You can send file without this command."
        "\n"
        f"{CommandsNames.UPLOAD_AUDIO.value} — upload an audio. "
        "Original name will be saved, original type may be changed. "
        "You can send audio file without this command."
        "\n"
        f"{CommandsNames.UPLOAD_VIDEO.value} — upload a video. "
        "Original name will be not saved, original type may be changed. "
        "You can send video file without this command."
        "\n"
        f"{CommandsNames.UPLOAD_VOICE.value} — upload a voice. "
        "You can send voice file without this command."
        "\n"
        f"{CommandsNames.UPLOAD_URL.value} — upload a file using direct URL. "
        "Original name will be saved. "
        "You can send direct URL to a file without this command."
        "\n"
        f"{CommandsNames.CREATE_FOLDER.value}— create a folder. "
        "Send folder name to create with this command. "
        "Folder name should starts from root, "
        f'nested folders should be separated with "{to_code("/")}" character.'
        "\n\n"
        "<b>Yandex.Disk Access</b>"
        "\n"
        f"{CommandsNames.YD_AUTH.value} — grant me access to your Yandex.Disk"
        "\n"
        f"{CommandsNames.YD_REVOKE.value} — revoke my access to your Yandex.Disk"
        "\n\n"
        "<b>Settings</b>"
        "\n"
        f"{CommandsNames.SETTINGS.value} — edit your settings"
        "\n\n"
        "<b>Information</b>"
        "\n"
        f"{CommandsNames.ABOUT.value} — read about me"
    )

    telegram.send_message(
        chat_id=g.telegram_chat.id,
        parse_mode="HTML",
        text=text
    )


def to_code(text: str) -> str:
    return f"<code>{text}</code>"
