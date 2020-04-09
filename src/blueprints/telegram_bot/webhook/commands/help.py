from flask import g, current_app

from .....api import telegram
from .common.names import CommandNames


def handle():
    """
    Handles `/help` command.
    """
    yd_upload_default_folder = current_app.config[
        "YANDEX_DISK_API_DEFAULT_UPLOAD_FOLDER"
    ]

    text = (
        "I can help you to interact with Yandex.Disk."
        "\n\n"
        "Send me some data (images, files, etc.) and "
        "i think i will handle this. "
        "Moreover, you can control me by sending these commands:"
        "\n\n"
        "<b>Yandex.Disk</b>"
        "\n"
        f'By default "<code>{yd_upload_default_folder}</code>" folder is used.'
        "\n"
        f"{CommandNames.UPLOAD_PHOTO.value} — uploads a photo. "
        "Original name will be not saved, quality of photo will be decreased. "
        "Send photo(s) with this command."
        "\n"
        f"{CommandNames.UPLOAD_FILE.value} — uploads a file. "
        "Original name will be saved. "
        "For photos, original quality will be saved. "
        "Send file(s) with this command."
        "\n"
        f"{CommandNames.UPLOAD_AUDIO.value} — uploads an audio. "
        "Send audio file(s) with this command."
        "\n"
        f"{CommandNames.UPLOAD_VIDEO.value} — uploads a video. "
        "Original name will be not saved. "
        "Send video file(s) with this command."
        "\n"
        f"{CommandNames.CREATE_FOLDER.value}— creates a folder. "
        "Send folder name with this command. "
        "Folder name should starts from root, "
        'nested folders should be separated with "<code>/</code>" character.'
        "\n\n"
        "<b>Yandex.Disk Access</b>"
        "\n"
        f"{CommandNames.YD_AUTH.value} — give me an access to your Yandex.Disk"
        "\n"
        f"{CommandNames.YD_REVOKE.value} — revoke my access to your Yandex.Disk" # noqa
        "\n\n"
        "<b>Settings</b>"
        "\n"
        f"{CommandNames.SETTINGS.value} — full list of settings"
        "\n\n"
        "<b>Information</b>"
        "\n"
        f"{CommandNames.ABOUT.value} — read about me"
    )

    telegram.send_message(
        chat_id=g.incoming_chat["id"],
        parse_mode="HTML",
        text=text
    )
