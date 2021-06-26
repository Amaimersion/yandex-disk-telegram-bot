from flask import g, current_app

from src.api import telegram
from src.i18n import gettext
from src.blueprints._common.utils import absolute_url_for


def handle(*args, **kwargs):
    """
    Handles `/about` command.
    """
    telegram.send_message(
        chat_id=kwargs.get(
            "chat_id",
            g.telegram_chat.id
        ),
        disable_web_page_preview=True,
        text=gettext(
            "I'm free and open-source bot that allows "
            "you to interact with Yandex.Disk through Telegram."
            "\n\n"
            "Written by %(author)s",
            author=current_app.config["PROJECT_AUTHOR"]
        ),
        reply_markup={"inline_keyboard": [
            [
                {
                    "text": gettext("Source code"),
                    "url": current_app.config['PROJECT_URL_FOR_CODE']
                }
            ],
            [
                {
                    "text": gettext("Report a problem"),
                    "url": current_app.config["PROJECT_URL_FOR_ISSUE"]
                },
                {
                    "text": gettext("Request a feature"),
                    "url": current_app.config["PROJECT_URL_FOR_REQUEST"]
                },
                {
                    "text": gettext("Ask a question"),
                    "url": current_app.config["PROJECT_URL_FOR_QUESTION"]
                }
            ],
            [
                {
                    "text": gettext("Privacy Policy"),
                    "url": absolute_url_for("legal.privacy_policy")
                },
                {
                    "text": gettext("Terms of service"),
                    "url": absolute_url_for("legal.terms_and_conditions")
                }
            ]
        ]}
    )
