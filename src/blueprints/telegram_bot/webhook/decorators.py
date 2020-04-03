from functools import wraps

from flask import g

from ....db import (
    db,
    User,
    UserQuery,
    Chat,
    ChatQuery
)
from ....db.models import (
    ChatType
)
from ....api import telegram


def register_guest(func):
    """
    Checks if incoming user exists in DB.
    If not, then that user will be created and saved.

    Rows will be created in next tables: `users`, `chats`.
    """
    # TODO: check if user came from different chat,
    # then also register that chat in db.

    @wraps(func)
    def wrapper(*args, **kwargs):
        incoming_user = g.incoming_user
        incoming_chat = g.incoming_chat

        if (UserQuery.exists(incoming_user["id"])):
            return func(*args, **kwargs)

        new_user = User(
            telegram_id=incoming_user["id"],
            is_bot=incoming_user.get("is_bot", False)
        )
        Chat(
            telegram_id=incoming_chat["id"],
            type=ChatType.get(incoming_chat["type"]),
            user=new_user
        )

        db.session.add(new_user)

        try:
            db.session.commit()
        except Exception as e:
            print(e)

            telegram.send_message(
                chat_id=incoming_chat["id"],
                text=(
                    "Can't process you because of internal error. "
                    "Try later please."
                )
            )

            return

        return func(*args, **kwargs)

    return wrapper


def get_db_data(func):
    """
    Gets data from DB based on `g.incoming_user` and
    `g.incoming_chat`. Data can be `None` if incoming
    data not exists in DB.

    DB data will be available as: `g.db_user`, `g.db_chat`.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.db_user = UserQuery.get_user_by_telegram_id(
            g.incoming_user["id"]
        )
        g.db_chat = ChatQuery.get_chat_by_telegram_id(
            g.incoming_chat["id"]
        )

        return func(*args, **kwargs)

    return wrapper
