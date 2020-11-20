from flask import g, current_app

from src.api import telegram
from src.api.yandex import make_photo_preview_request
from src.blueprints.telegram_bot._common.yandex_disk import (
    get_element_info,
    YandexAPIGetElementInfoError,
    YandexAPIRequestError
)
from src.blueprints.telegram_bot._common.stateful_chat import (
    set_disposable_handler
)
from src.blueprints.telegram_bot._common.command_names import (
    CommandName
)
from src.blueprints.telegram_bot.webhook.dispatcher_events import (
    DispatcherEvent
)
from ._common.responses import (
    cancel_command,
    request_absolute_path,
    send_yandex_disk_error
)
from ._common.decorators import (
    yd_access_token_required,
    get_db_data
)
from ._common.utils import (
    extract_absolute_path,
    create_element_info_html_text
)


@yd_access_token_required
@get_db_data
def handle(*args, **kwargs):
    """
    Handles `/element_info` command.
    """
    message = kwargs.get(
        "message",
        g.telegram_message
    )
    user_id = kwargs.get(
        "user_id",
        g.telegram_user.id
    )
    chat_id = kwargs.get(
        "chat_id",
        g.telegram_chat.id
    )
    path = extract_absolute_path(
        message,
        CommandName.ELEMENT_INFO.value,
        kwargs.get("route_source")
    )

    if not path:
        set_disposable_handler(
            user_id,
            chat_id,
            CommandName.ELEMENT_INFO.value,
            [
                DispatcherEvent.PLAIN_TEXT.value,
                DispatcherEvent.BOT_COMMAND.value,
                DispatcherEvent.EMAIL.value,
                DispatcherEvent.HASHTAG.value,
                DispatcherEvent.URL.value
            ],
            current_app.config["RUNTIME_DISPOSABLE_HANDLER_EXPIRE"]
        )

        return request_absolute_path(chat_id)

    user = g.db_user
    access_token = user.yandex_disk_token.get_access_token()
    info = None

    try:
        info = get_element_info(access_token, path)
    except YandexAPIRequestError as error:
        cancel_command(chat_id)
        raise error
    except YandexAPIGetElementInfoError as error:
        send_yandex_disk_error(chat_id, str(error))

        # it is expected error and should be
        # logged only to user
        return

    text = create_element_info_html_text(info, True)
    params = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    download_url = info.get("file")

    if download_url:
        params["reply_markup"] = {
            "inline_keyboard": [[
                {
                    "text": "Download",
                    "url": download_url
                }
            ]]
        }

    telegram.send_message(**params)

    preview = info.get("preview")

    if preview:
        # Yandex requires user OAuth token to get preview
        result = make_photo_preview_request(preview, access_token)

        if result["ok"]:
            data = result["content"]
            filename = info.get("name", "?")

            telegram.send_photo(
                chat_id=chat_id,
                photo=(
                    filename,
                    data,
                    "image/jpeg"
                ),
                disable_notification=True
            )
