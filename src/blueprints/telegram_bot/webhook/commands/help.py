from flask import g

from .....api import telegram


def handle():
    """
    Handles `/help` command.
    """
    text = (
        "I can help you to interact with Yandex.Disk."
        "\n\n"
        "Send me some data (images, files, etc.) and "
        "i think i will handle this. "
        "Moreover, you can control me by sending these commands:"
        "\n\n"
        "<b>Yandex.Disk</b>"
        "\n"
        "/upload_photo — uploads a photo"
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
