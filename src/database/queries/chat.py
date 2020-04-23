from typing import List, Union, NewType

from src.database import Chat
from src.database.models import ChatType


ChatOrNone = NewType("ChatOrNone", Union[Chat, None])


def delete_all_chats() -> int:
    """
    Deletes all chats from a table.

    - you have to commit DB changes!

    :returns: Count of deleted chats.
    """
    return Chat.query.delete()


def get_private_chat(user_id: int) -> ChatOrNone:
    """
    Returns private chat of user.

    :param user_id: ID of user.
    """
    return Chat.query.filter(
        Chat.user_id == user_id,
        Chat.type == ChatType.PRIVATE
    ).first()


def get_chat_by_telegram_id(telegram_id: int) -> ChatOrNone:
    """
    Returns chat with specified telegram id.
    """
    return Chat.query.filter(Chat.telegram_id == telegram_id).first()
