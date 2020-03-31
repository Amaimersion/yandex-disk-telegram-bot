from typing import List, Union, NewType

from .. import Chat
from ..models import ChatType


ChatOrNone = NewType("ChatOrNone", Union[Chat, None])


def delete_all_chats() -> int:
    """
    Deletes all chats from a table.

    You have to commit DB changes!

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
