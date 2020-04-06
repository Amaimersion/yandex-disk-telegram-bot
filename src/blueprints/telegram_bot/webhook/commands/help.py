from flask import g, current_app

from .....api import telegram


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
        "/upload_photo — uploads a photo with quality loss. "
        "Send photos or photos with this command. "
        f"By default `{yd_upload_default_folder}` folder is used."
        "\n"
        "/create_folder — creates a folder. "
        "Send folder name with this command. "
        "Folder name should starts from root, "
        "nested folders should be separated with `/` character."
        "\n\n"
        "<b>Yandex.Disk Access</b>"
        "\n"
        "/yandex_disk_authorization — give me an access to your Yandex.Disk"
        "\n"
        "/yandex_disk_revoke — revoke my access to your Yandex.Disk"
        "\n\n"
        "<b>Settings</b>"
        "\n"
        "/settings — full list of settings"
        "\n\n"
        "<b>Information</b>"
        "\n"
        "/about — read about me"
    )

    telegram.send_message(
        chat_id=g.incoming_chat["id"],
        parse_mode="HTML",
        text=text
    )
