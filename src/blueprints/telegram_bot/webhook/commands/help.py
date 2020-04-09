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
        f'By default "<code>{yd_upload_default_folder}</code>" folder is used.'
        "\n"
        "/upload_photo — uploads a photo. "
        "Original name will be not saved, quality of photo will be decreased. "
        "Send photo(s) with this command."
        "\n"
        "/upload_file — uploads a file. "
        "Original name will be saved. "
        "For photos, original quality will be saved. "
        "Send file(s) with this command."
        "\n"
        "/create_folder — creates a folder. "
        "Send folder name with this command. "
        "Folder name should starts from root, "
        'nested folders should be separated with "<code>/</code>" character.'
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
