# flake8: noqa

from flask import g, current_app

from src.api import telegram
from src.blueprints.telegram_bot._common.command_names import CommandName


def handle(*args, **kwargs):
    """
    Handles `/help` command.
    """
    yd_upload_default_folder = current_app.config[
        "YANDEX_DISK_API_DEFAULT_UPLOAD_FOLDER"
    ]
    file_size_limit_in_mb = int(current_app.config[
        "TELEGRAM_API_MAX_FILE_SIZE"
    ] / 1024 / 1024)

    text = (
        "You can control me by sending these commands:"
        "\n\n"
        "<b>Yandex.Disk</b>"
        "\n"
        f'For uploading "{to_code(yd_upload_default_folder)}" folder is used by default.'
        "\n"
        f'Maximum size of every upload (except URL) is {file_size_limit_in_mb} MB.'
        "\n"
        f"{CommandName.UPLOAD_PHOTO.value} — upload a photo. "
        "Original name will be not saved, quality of photo will be decreased. "
        "You can send photo without this command. "
        f"Use {CommandName.PUBLIC_UPLOAD_PHOTO.value} for public uploading."
        "\n"
        f"{CommandName.UPLOAD_FILE.value} — upload a file. "
        "Original name will be saved. "
        "For photos, original quality will be saved. "
        "You can send file without this command. "
        f"Use {CommandName.PUBLIC_UPLOAD_FILE.value} for public uploading."
        "\n"
        f"{CommandName.UPLOAD_AUDIO.value} — upload an audio. "
        "Original name will be saved, original type may be changed. "
        "You can send audio file without this command. "
        f"Use {CommandName.PUBLIC_UPLOAD_AUDIO.value} for public uploading."
        "\n"
        f"{CommandName.UPLOAD_VIDEO.value} — upload a video. "
        "Original name will be saved, original type may be changed. "
        "You can send video file without this command. "
        f"Use {CommandName.PUBLIC_UPLOAD_VIDEO.value} for public uploading."
        "\n"
        f"{CommandName.UPLOAD_VOICE.value} — upload a voice. "
        "You can send voice file without this command. "
        f"Use {CommandName.PUBLIC_UPLOAD_VOICE.value} for public uploading."
        "\n"
        f"{CommandName.UPLOAD_URL.value} — upload a file using direct URL. "
        "Original name will be saved. "
        "You can send direct URL to a file without this command. "
        f"Use {CommandName.PUBLIC_UPLOAD_URL.value} for public uploading."
        "\n"
        f"{CommandName.PUBLISH.value} — publish a file or folder that already exists. "
        "Send full name of item to publish with this command. "
        f'Example: {to_code(f"/{yd_upload_default_folder}/files/photo.jpeg")}'
        "\n"
        f"{CommandName.UNPUBLISH.value} — unpublish a file or folder that already exists. "
        "Send full name of item to unpublish with this command. "
        f'Example: {to_code(f"/{yd_upload_default_folder}/files/photo.jpeg")}'
        "\n"
        f"{CommandName.CREATE_FOLDER.value} — create a folder. "
        "Send folder name to create with this command. "
        "Folder name should starts from root, "
        f'nested folders should be separated with "{to_code("/")}" character.'
        "\n"
        f"{CommandName.SPACE.value} — get information about remaining space."
        "\n"
        f"{CommandName.ELEMENT_INFO.value} — get information about file or folder. "
        "Send full path of element with this command."
        "\n\n"
        "<b>Yandex.Disk Access</b>"
        "\n"
        f"{CommandName.YD_AUTH.value} — grant me access to your Yandex.Disk"
        "\n"
        f"{CommandName.YD_REVOKE.value} — revoke my access to your Yandex.Disk"
        "\n\n"
        "<b>Settings</b>"
        "\n"
        f"{CommandName.SETTINGS.value} — edit your settings"
        "\n\n"
        "<b>Information</b>"
        "\n"
        f"{CommandName.ABOUT.value} — read about me"
    )

    chat_id = kwargs.get(
        "chat_id",
        g.telegram_chat.id
    )
    telegram.send_message(
        chat_id=chat_id,
        parse_mode="HTML",
        text=text
    )


def to_code(text: str) -> str:
    return f"<code>{text}</code>"
