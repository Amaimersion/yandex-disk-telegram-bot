from functools import wraps

from flask import g

from src.extensions import db
from src.database import (
    User,
    UserQuery,
    Chat,
    ChatQuery,
    UserSettings
)
from src.database.models import (
    ChatType
)
from src.localization import SupportedLanguage
from src.blueprints.telegram_bot._common.command_names import CommandName
from .responses import cancel_command


def register_guest(func):
    """
    If incoming Telegram user doesn't exists in DB,
    then that user will be created and saved.

    - rows will be created in next tables: `users`, `chats`
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        tg_user = g.telegram_user
        tg_chat = g.telegram_chat

        # TODO: check if user came from different chat,
        # then also register that chat in db.
        if (UserQuery.exists(tg_user.id)):
            return func(*args, **kwargs)

        new_user = User(
            telegram_id=tg_user.id,
            is_bot=tg_user.is_bot
        )
        UserSettings(
            user=new_user,
            language=SupportedLanguage.get(tg_user.language_code or "")
        )
        Chat(
            telegram_id=tg_chat.id,
            type=ChatType.get(tg_chat.type),
            user=new_user
        )

        db.session.add(new_user)

        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return cancel_command(tg_chat.id)

        return func(*args, **kwargs)

    return wrapper


def yd_access_token_required(func):
    """
    Checks if incoming user have Yandex.Disk access token.
    If not, then that user will be redirected to another
    command for getting Y.D. token.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = UserQuery.get_user_by_telegram_id(
            g.telegram_user.id
        )

        # TODO: check if token is expired
        if (
            (user is None) or
            (user.yandex_disk_token is None) or
            (not user.yandex_disk_token.have_access_token())
        ):
            return g.direct_dispatch(CommandName.YD_AUTH)()

        return func(*args, **kwargs)

    return wrapper
