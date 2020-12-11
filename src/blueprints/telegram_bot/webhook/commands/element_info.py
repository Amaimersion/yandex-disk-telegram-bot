from flask import g, current_app

from src.extensions import task_queue
from src.api import telegram
from src.api.yandex import make_photo_preview_request
from src.blueprints.telegram_bot._common.yandex_disk import (
    get_element_info,
    YandexAPIGetElementInfoError,
    YandexAPIRequestError
)
from src.blueprints.telegram_bot._common.stateful_chat import (
    stateful_chat_is_enabled,
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
        if stateful_chat_is_enabled():
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
        info = get_element_info(
            access_token,
            path,
            get_public_info=True
        )
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

    # We will send message without preview,
    # because it can take a while to download
    # preview file and send it. We will
    # send it later if it is available.
    telegram.send_message(**params)

    preview_url = info.get("preview")

    if preview_url:
        filename = info.get("name", "preview.jpg")
        arguments = (
            preview_url,
            filename,
            access_token,
            chat_id
        )

        if task_queue.is_enabled:
            job_timeout = current_app.config[
                "RUNTIME_ELEMENT_INFO_WORKER_JOB_TIMEOUT"
            ]
            ttl = current_app.config[
                "RUNTIME_ELEMENT_INFO_WORKER_TTL"
            ]

            task_queue.enqueue(
                send_preview,
                args=arguments,
                description=CommandName.ELEMENT_INFO.value,
                job_timeout=job_timeout,
                ttl=ttl,
                result_ttl=0,
                failure_ttl=0
            )
        else:
            # NOTE: current thread will
            # be blocked for a while
            send_preview(*arguments)


def send_preview(
    preview_url: str,
    filename: str,
    user_access_token: str,
    chat_id: int
):
    """
    Downloads preview from Yandex.Disk and sends it to user.

    - requires user Yandex.Disk access token to
    download preview file.
    """
    result = make_photo_preview_request(
        preview_url,
        user_access_token
    )

    if result["ok"]:
        data = result["content"]

        telegram.send_photo(
            chat_id=chat_id,
            photo=(
                filename,
                data,
                "image/jpeg"
            ),
            disable_notification=True
        )
