from abc import ABCMeta, abstractmethod
from enum import unique, auto
from typing import Any, Tuple, Union

from flask import g, current_app

from src.api import telegram
from src.extensions import db
from src.database import User, UserSettings
from src.blueprints._common.utils import EnumStrAutoName
from src.blueprints.telegram_bot._common.yandex_oauth import (
    YandexOAuthClient
)
from src.blueprints.telegram_bot._common.reply_markup import (
    create_callback_data
)
from src.blueprints.telegram_bot._common.command_names import (
    CommandName
)
from src.blueprints.telegram_bot._common.stateful_chat import (
    stateful_chat_is_enabled,
    set_disposable_handler,
    get_disposable_handler,
    set_user_chat_data,
    get_user_chat_data,
    delete_user_chat_data
)
from src.blueprints.telegram_bot.webhook.dispatcher_interface import (
    RouteSource,
    DispatcherEvent
)
from ._common.decorators import (
    register_guest,
    get_db_data
)
from ._common.responses import (
    request_private_chat,
    request_absolute_folder_name,
    cancel_command
)


@unique
class UserAction(EnumStrAutoName):
    """
    What action did the user dispatch.
    """
    CHANGE_DEFAULT_UPLOAD_FOLDER = auto()


class CallbackQueryData:
    """
    Data of callback query request.
    """
    def __init__(
        self,
        chat_id: str,
        message_id: int,
        callback_query_id: str,
        user: User,
        payload: Any
    ):
        self.chat_id = chat_id
        self.message_id = message_id
        self.callback_query_id = callback_query_id
        self.user = user
        self.payload = payload


class DisposableHandlerData:
    """
    Data of disposable handler request.
    """
    def __init__(
        self,
        chat_id: str,
        user: User,
        message_text: str,
        last_message_id: int = None
    ):
        self.chat_id = chat_id
        self.user = user
        self.user_settings: UserSettings = user.settings
        self.message_text = message_text
        self.last_message_id = last_message_id


class UserActionHandler(metaclass=ABCMeta):
    """
    Base class for action handlers.

    - stateful chat is required to be enabled
    """
    @staticmethod
    def set_last_action(
        user_id: str,
        chat_id: str,
        user_last_action: str
    ) -> None:
        """
        Remembers user last action.
        For example, if user clicked on "Change folder" button,
        then last action will be "click on change folder button".
        """
        set_user_chat_data(
            user_id,
            chat_id,
            "settings_last_action",
            user_last_action,
            current_app.config["RUNTIME_SETTINGS_LAST_ACTION_EXPIRE"]
        )

    @staticmethod
    def get_last_action(
        user_id: str,
        chat_id: str
    ) -> str:
        """
        :returns:
        User last action.
        """
        return get_user_chat_data(
            user_id,
            chat_id,
            "settings_last_action"
        )

    @staticmethod
    def delete_last_action(
        user_id: str,
        chat_id: str
    ) -> None:
        """
        Removes user last action.
        """
        delete_user_chat_data(
            user_id,
            chat_id,
            "settings_last_action"
        )

    @staticmethod
    def set_last_message_id(
        user_id: str,
        chat_id: str,
        message_id: int
    ) -> None:
        """
        Remembers provided value as last message id.
        """
        set_user_chat_data(
            user_id,
            chat_id,
            "settings_last_message_id",
            message_id,
            current_app.config["RUNTIME_SETTINGS_LAST_ACTION_EXPIRE"]
        )

    @staticmethod
    def get_last_message_id(
        user_id: str,
        chat_id: str
    ) -> int:
        """
        :returns:
        Last message id.
        """
        return int(get_user_chat_data(
            user_id,
            chat_id,
            "settings_last_message_id"
        ))

    @staticmethod
    def delete_last_message_id(
        user_id: str,
        chat_id: str
    ) -> None:
        """
        Removes last message id.
        """
        delete_user_chat_data(
            user_id,
            chat_id,
            "settings_last_message_id"
        )

    @staticmethod
    def set_disposable_handler(
        user_id: str,
        chat_id: str,
        events: Tuple[DispatcherEvent]
    ) -> None:
        """
        Sets disposable handler.

        For example, next time when user will send plain text message,
        dispatcher will dispatch a message to specific handler.
        """
        set_disposable_handler(
            user_id,
            chat_id,
            CommandName.SETTINGS.value,
            events,
            current_app.config["RUNTIME_SETTINGS_LAST_ACTION_EXPIRE"]
        )

    @property
    @abstractmethod
    def user_action(self) -> UserAction:
        """
        :returns:
        What action this handler handles.
        """
        pass

    @property
    @abstractmethod
    def disposable_handler_events(self) -> Tuple[DispatcherEvent]:
        """
        :returns:
        At what events disposable handler should be called.
        For example, next plain text message should be
        redirected to that handler.
        """
        pass

    @abstractmethod
    def on_callback_query_data(self, data: CallbackQueryData) -> None:
        """
        Will be called when user will press on callback query button.
        Actual logic should go here.
        """
        pass

    @abstractmethod
    def on_disposable_handler(self, data: DisposableHandlerData) -> None:
        """
        Will be called when dispatcher will call this
        handler as disposable handler.
        Actual logic should go here.
        """
        pass

    def handle_callback_query_data(self, data: CallbackQueryData) -> None:
        """
        Handles press on callback query button.

        :param data:
        Data of callback query request.
        """
        self.before_callback_query_data(data)
        self.on_callback_query_data(data)
        self.after_callback_query_data(data)

    def before_callback_query_data(self, data: CallbackQueryData) -> None:
        """
        Will be called before handling of callback query button.
        """
        self.set_last_action(
            data.user.telegram_id,
            data.chat_id,
            self.user_action.value
        )
        self.set_last_message_id(
            data.user.telegram_id,
            data.chat_id,
            data.message_id
        )
        self.set_disposable_handler(
            data.user.telegram_id,
            data.chat_id,
            self.disposable_handler_events
        )
        self.answer_callback_query(
            data.callback_query_id
        )

    def after_callback_query_data(self, data: CallbackQueryData) -> None:
        """
        Will be called after handling of callback query button.
        """
        pass

    def handle_disposable_handler(self, data: DisposableHandlerData) -> None:
        """
        Handles disposable handler event.

        :param data:
        Data of disposable handler request.
        """
        self.before_disposable_handler(data)
        self.on_disposable_handler(data)
        self.after_disposable_handler(data)

    def before_disposable_handler(self, data: DisposableHandlerData) -> None:
        """
        Will be called before handling of disposable handler event.
        """
        data.last_message_id = self.get_last_message_id(
            data.user.telegram_id,
            data.chat_id
        )

    def after_disposable_handler(self, data: DisposableHandlerData) -> None:
        """
        Will be called after handling of disposable handler event.
        """
        self.delete_last_action(
            data.user.telegram_id,
            data.chat_id
        )
        self.delete_last_message_id(
            data.user.telegram_id,
            data.chat_id
        )

    def answer_callback_query(
        self,
        callback_query_id: str
    ) -> None:
        """
        Answers on callback query event.

        From Telegram documentation:
        "After the user presses a callback button,
        Telegram clients will display a progress bar until you
        call answerCallbackQuery. It is, therefore, necessary to
        react by calling answerCallbackQuery even if no notification
        to the user is needed."
        """
        telegram.answer_callback_query(
            callback_query_id=callback_query_id
        )

    def db_commit(self) -> None:
        """
        Performs DB commit.
        """
        db.session.commit()


class ChangeDefaultUploadFolderHandler(UserActionHandler):
    """
    Changing of default upload folder.
    """
    @property
    def user_action(self):
        return UserAction.CHANGE_DEFAULT_UPLOAD_FOLDER

    @property
    def disposable_handler_events(self):
        return (
            DispatcherEvent.PLAIN_TEXT.value,
            DispatcherEvent.BOT_COMMAND.value,
            DispatcherEvent.HASHTAG.value,
            DispatcherEvent.EMAIL.value
        )

    def on_callback_query_data(self, data: CallbackQueryData) -> None:
        request_absolute_folder_name(
            data.chat_id,
            "a new path of default upload folder"
        )

    def on_disposable_handler(self, data: DisposableHandlerData) -> None:
        old_value = data.user_settings.default_upload_folder
        new_value = data.message_text
        need_to_change = (old_value != new_value)
        need_to_send_current_settings = False
        response_text = ""

        if need_to_change:
            try:
                data.user_settings.default_upload_folder = new_value
                self.db_commit()
            except Exception as error:
                print(error)
                return cancel_command(data.chat_id)

            response_text = (
                "Success."
                "\n"
                f"<code>{old_value}</code> was changed to "
                f"<code>{new_value}</code>"
            )
            need_to_send_current_settings = True
        else:
            response_text = "Success."

        telegram.send_message(
            chat_id=data.chat_id,
            parse_mode="HTML",
            text=response_text
        )

        if need_to_send_current_settings:
            send_current_settings(
                data.chat_id,
                data.user,
                data.last_message_id
            )


@register_guest
@get_db_data
def handle(*args, **kwargs):
    """
    Handles `/settings` command.
    """
    private_chat = g.db_private_chat

    if private_chat is None:
        incoming_chat_id = kwargs.get(
            "chat_id",
            g.db_chat.telegram_id
        )

        return request_private_chat(incoming_chat_id)

    chat_id = private_chat.telegram_id
    user = g.db_user
    message = kwargs.get("message")
    route_source = kwargs.get("route_source")
    callback_query = kwargs.get("callback_query")
    callback_query_data = kwargs.get("callback_query_data")

    if (route_source == RouteSource.CALLBACK_QUERY_DATA):
        request_data = CallbackQueryData(
            chat_id,
            callback_query.get_message().message_id,
            callback_query.id,
            user,
            callback_query_data
        )
        dispatch_callback_query_data_request(request_data)
    elif (route_source == RouteSource.DISPOSABLE_HANDLER):
        request_data = DisposableHandlerData(
            chat_id,
            user,
            message.get_text()
        )
        dispatch_disposable_handler_request(request_data)
    else:
        handle_direct_command(
            chat_id,
            user
        )


def dispatch_callback_query_data_request(data: CallbackQueryData) -> None:
    """
    Dispatches callback query data request to specific action handler.

    - usually callback query data means user clicked on an inline button
    - stateful chat is required to be enabled
    """
    if not stateful_chat_is_enabled():
        telegram.answer_callback_query(
            callback_query_id=data.callback_query_id
        )
        cancel_command(data.chat_id)

        return

    handler = get_user_action_handler(data.payload)

    if handler:
        handler.handle_callback_query_data(data)


def dispatch_disposable_handler_request(data: DisposableHandlerData) -> None:
    """
    Dispatches disposable handler request to specific action handler.

    - usually this stage means user sent a data he was asked for
    - stateful chat is required to be enabled
    """
    if not stateful_chat_is_enabled():
        raise Exception("Stateful chat is required to be enabled")

    last_action = UserActionHandler.get_last_action(
        data.user.telegram_id,
        data.chat_id
    )
    handler = get_user_action_handler(last_action)

    if handler:
        handler.handle_disposable_handler(data)


def get_user_action_handler(
    user_action_value: str
) -> Union[UserActionHandler, None]:
    """
    :param user_action_value:
    Value of `UserAction` enum.

    :returns:
    Most appropriate handler that matches to `user_action_value`.
    `None` will be returned if nothing matches.
    """
    handlers = {
        UserAction.CHANGE_DEFAULT_UPLOAD_FOLDER.value: (
            ChangeDefaultUploadFolderHandler
        )
    }
    ActionHandler = handlers.get(user_action_value)
    handler = ActionHandler()

    return handler


def handle_direct_command(
    chat_id: str,
    user: User
) -> None:
    """
    Handles direct command.
    """
    send_current_settings(chat_id, user)


def send_current_settings(
    chat_id: str,
    user: User,
    message_id: int = None
) -> None:
    """
    Sends user current settings.

    :param chat_id:
    Telegram ID of char.
    :param user:
    DB user.
    :param message_id:
    Telegram ID of message.
    Defaults to `None`.
    If specified, then that message will be
    edited instead of sending new one.
    """
    settings: UserSettings = user.settings
    yo_client = YandexOAuthClient()
    yd_access = False

    if yo_client.have_valid_access_token(user):
        yd_access = True

    text = (
        "<b>Default upload folder:</b> "
        f"<code>{settings.default_upload_folder}</code>"
        "\n"
        "<b>Preferred language:</b> "
        f"{user.language.name}"
        "\n"
        "<b>Yandex.Disk Access:</b> "
        f"{'Given' if yd_access else 'Revoked'}"
    )
    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "Change default upload folder",
                    "callback_data": create_callback_data(
                        [CommandName.SETTINGS],
                        UserAction.CHANGE_DEFAULT_UPLOAD_FOLDER.value
                    )
                }
            ]
        ]
    }
    kwargs = {
        "parse_mode": "HTML",
        "chat_id": chat_id,
        "text": text,
        "reply_markup": reply_markup
    }

    if message_id is not None:
        telegram.edit_message_text(
            **kwargs,
            message_id=message_id
        )
    else:
        telegram.send_message(**kwargs)
