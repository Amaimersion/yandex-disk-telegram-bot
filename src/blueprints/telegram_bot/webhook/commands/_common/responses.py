from enum import IntEnum, unique

from flask import current_app

from src.http import telegram
from src.i18n import gettext


@unique
class AbortReason(IntEnum):
    """
    Reason for `abort_command`.
    """
    UNKNOWN = 1
    NO_SUITABLE_DATA = 2
    EXCEED_FILE_SIZE_LIMIT = 3


def abort_command(
    chat_telegram_id: int,
    reason: AbortReason,
    edit_message: int = None,
    reply_to_message: int = None
) -> None:
    """
    Aborts command execution due to invalid message data.

    - don't confuse with `cancel_command()`.
    - if `edit_message` Telegram ID specified, then
    that message will be edited.
    - if `reply_to_message` Telegram ID specified, then
    that message will be used for reply message.
    """
    texts = {
        AbortReason.UNKNOWN: gettext(
            "I can't handle this because something is wrong."
        ),
        AbortReason.NO_SUITABLE_DATA: gettext(
            "I can't handle this because "
            "you didn't send any suitable data "
            "for that command."
        ),
        AbortReason.EXCEED_FILE_SIZE_LIMIT: gettext(
            "I can't handle file of such a large size. "
            "At the moment my limit is "
            "%(limit_in_mb)s MB.",
            limit_in_mb=(
                current_app.config['TELEGRAM_API_MAX_FILE_SIZE'] / 1024 / 1024
            )
        )
    }
    text = texts[reason]

    if (edit_message is not None):
        telegram.edit_message_text(
            chat_id=chat_telegram_id,
            message_id=edit_message,
            text=text
        )
    elif (reply_to_message is not None):
        telegram.send_message(
            chat_id=chat_telegram_id,
            reply_to_message_id=reply_to_message,
            text=text
        )
    else:
        telegram.send_message(
            chat_id=chat_telegram_id,
            text=text
        )


def cancel_command(
    chat_telegram_id: int,
    edit_message: int = None,
    reply_to_message: int = None
) -> None:
    """
    Cancels command execution due to internal server error.

    - don't confuse with `abort_command()`.
    - if `edit_message` Telegram ID specified, then
    that message will be edited.
    - if `reply_to_message` Telegram ID specified, then
    that message will be used for reply message.
    """
    text = gettext(
        "At the moment i can't process this "
        "because of my internal error. "
        "Try later please."
    )
    reply_markup = {}
    url_for_issue = current_app.config.get('PROJECT_URL_FOR_ISSUE')

    if url_for_issue:
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": gettext("Report a problem"),
                        "url": url_for_issue
                    }
                ]
            ]
        }

    if (edit_message is not None):
        telegram.edit_message_text(
            chat_id=chat_telegram_id,
            message_id=edit_message,
            text=text,
            reply_markup=reply_markup
        )
    elif (reply_to_message is not None):
        telegram.send_message(
            chat_id=chat_telegram_id,
            reply_to_message_id=reply_to_message,
            text=text,
            reply_markup=reply_markup
        )
    else:
        telegram.send_message(
            chat_id=chat_telegram_id,
            text=text,
            reply_markup=reply_markup
        )


def request_private_chat(chat_telegram_id: int) -> None:
    """
    Aborts command execution due to lack of private chat with user.
    """
    telegram.send_message(
        chat_id=chat_telegram_id,
        text=gettext(
            "I need to send you your secret information, "
            "but i don't know any private chat with you. "
            "First, contact me through private chat (direct message). "
            "After that repeat your request."
        )
    )


def send_yandex_disk_error(
    chat_telegram_id: int,
    error_text: str,
    reply_to_message_id: int = None
) -> None:
    """
    Sends a message that indicates that Yandex.Disk threw an error.

    :param error_text:
    Text of error that will be printed.
    Can be empty.
    :param reply_to_message_id:
    If specified, then sended message will be a reply message.
    """
    unknown_error_text = gettext("Unknown")
    kwargs = {
        "chat_id": chat_telegram_id,
        "parse_mode": "HTML",
        "text": gettext(
            "<b>Yandex.Disk Error</b>"
            "\n\n"
            "%(error_text)s",
            error_text=(error_text or unknown_error_text)
        )
    }

    if reply_to_message_id is not None:
        kwargs["reply_to_message_id"] = reply_to_message_id

    telegram.send_message(**kwargs)


def request_absolute_path(chat_telegram_id: int) -> None:
    """
    Sends a message that asks a user to send an
    absolute path (folder or file).
    """
    separator = "/"
    path_1 = "Telegram Bot/kittens and raccoons"
    path_2 = "/Telegram Bot/kittens and raccoons/musya.jpg"

    telegram.send_message(
        chat_id=chat_telegram_id,
        parse_mode="HTML",
        text=gettext(
            "Send a full path."
            "\n\n"
            "It should starts from root directory, "
            "nested folders should be separated with "
            '"<code>%(separator)s</code>" character. '
            "In short, i expect an absolute path to the item."
            "\n\n"
            "Example: <code>%(path_1)s</code>"
            "\n"
            "Example: <code>%(path_2)s</code>",
            separator=separator,
            path_1=path_1,
            path_2=path_2
        )
    )


def request_absolute_folder_name(
    chat_telegram_id: int,
    folder_name=None
) -> None:
    """
    Sends a message that asks a user to send an
    absolute path of folder.

    :param folder_name:
    Name of folder which will be used in a message.
    See function source for template.
    """
    if folder_name is None:
        folder_name = gettext("a folder name")

    separator = "/"
    path_1 = "Telegram Bot/kittens and raccoons"

    telegram.send_message(
        chat_id=chat_telegram_id,
        parse_mode="HTML",
        text=gettext(
            "Send %(folder_name)s."
            "\n\n"
            "It should starts from root directory, "
            "nested folders should be separated with "
            '"<code>%(separator)s</code>" character. '
            "In short, i expect a full path."
            "\n\n"
            "Example: <code>%(path_1)s</code>",
            folder_name=folder_name,
            separator=separator,
            path_1=path_1
        )
    )
