from flask import g, current_app

from src.api import telegram
from src.blueprints.utils import absolute_url_for


def handle():
    """
    Handles `/about` command.
    """
    telegram.send_message(
        chat_id=g.telegram_chat.id,
        disable_web_page_preview=True,
        text=(
            "I'm free and open-source bot that allows "
            "you to interact with Yandex.Disk through Telegram."
            "\n\n"
            f"Written by {current_app.config['PROJECT_AUTHOR']}"
            "\n"
            f"{current_app.config['PROJECT_URL_FOR_CODE']}"
        ),
        reply_markup={"inline_keyboard": [
            [
                {
                    "text": "Post an issue",
                    "url": current_app.config["PROJECT_URL_FOR_ISSUE"]
                },
                {
                    "text": "Request a feature",
                    "url": current_app.config["PROJECT_URL_FOR_REQUEST"]
                },
                {
                    "text": "Ask a question",
                    "url": current_app.config["PROJECT_URL_FOR_QUESTION"]
                }
            ],
            [
                {
                    "text": "Privacy Policy",
                    "url": absolute_url_for("legal.privacy_policy")
                },
                {
                    "text": "Terms And Conditions",
                    "url": absolute_url_for("legal.terms_and_conditions")
                }
            ]
        ]}
    )
