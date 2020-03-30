from .. import Chat


def delete_all_chats() -> int:
    """
    Deletes all chats from a table.

    You have to commit DB changes!

    :returns: Count of deleted chats.
    """
    return Chat.query.delete()
