from typing import (
    List,
    Union,
    Any
)

from .commands import CommandsNames


class User:
    """
    Telegram user.

    https://core.telegram.org/bots/api/#user
    """
    def __init__(self, raw_data: dict) -> None:
        self.raw_data = raw_data

    @property
    def id(self) -> int:
        return self.raw_data["id"]

    @property
    def is_bot(self) -> bool:
        return self.raw_data["is_bot"]

    @property
    def language_code(self) -> Union[str, None]:
        return self.raw_data.get("language_code")


class Chat:
    """
    Telegram chat.

    https://core.telegram.org/bots/api/#chat
    """
    def __init__(self, raw_data: dict) -> None:
        self.raw_data = raw_data

    @property
    def id(self) -> int:
        return self.raw_data["id"]

    @property
    def type(self) -> str:
        return self.raw_data["type"]


class Entity:
    """
    Entity from Telegram message.

    https://core.telegram.org/bots/api/#messageentity
    """
    def __init__(self, raw_data: dict) -> None:
        self.raw_data = raw_data

    @property
    def type(self) -> str:
        return self.raw_data["type"]

    @property
    def offset(self) -> int:
        return self.raw_data["offset"]

    @property
    def length(self) -> int:
        return self.raw_data["length"]

    def is_bot_command(self) -> bool:
        """
        :returns: Entity is a bot command.
        """
        return (self.type == "bot_command")

    def is_url(self) -> bool:
        """
        :returns: Entity is an URL.
        """
        return (self.type == "url")


class Message:
    """
    Telegram message from user.

    https://core.telegram.org/bots/api/#message
    """
    def __init__(self, raw_data: dict) -> None:
        self.raw_data = raw_data
        self.entities: Union[List[Entity], None] = None

    @property
    def message_id(self) -> int:
        return self.raw_data["message_id"]

    def is_valid(self) -> bool:
        """
        :returns: Message is valid for handling.
        """
        return (
            isinstance(
                self.raw_data.get("from"),
                dict
            )
        )

    def get_user(self) -> str:
        """
        :returns: Who sent this message.
        """
        raw_data = self.raw_data["from"]

        return User(raw_data)

    def get_chat(self) -> Chat:
        """
        :returns: Where did this message come from.
        """
        raw_data = self.raw_data["chat"]

        return Chat(raw_data)

    def get_text(self) -> str:
        """
        :returns: Message text.
        """
        return (
            self.raw_data.get("text") or
            self.raw_data.get("caption") or
            ""
        )

    def get_entities(self) -> List[Entity]:
        """
        :returns: Entities from a message.
        """
        if (self.entities is None):
            self.entities = []
            entities = (
                self.raw_data.get("entities") or
                self.raw_data.get("caption_entities") or
                []
            )

            for entity in entities:
                self.entities.append(
                    Entity(entity)
                )

        return self.entities

    def get_entity_value(
        self,
        entity_type: str,
        default: Any = None
    ) -> Any:
        """
        Extracts value of single entity from a message.

        - first value will be returned, all others
        will be ignored.

        :param entity_type: Type of entity whose value
        you want to extract. See
        https://core.telegram.org/bots/api/#messageentity
        :param default: Default value which will be
        returned if no such entities in a message.

        :returns: First value or `default`.

        :raises ValueError: If `entity_type` not supported.
        """
        text = self.get_text()
        entities = self.get_entities()
        value = default
        checkers = {
            "bot_command": lambda entity: entity.is_bot_command(),
            "url": lambda entity: entity.is_url()
        }
        is_valid = checkers.get(entity_type)

        if (is_valid is None):
            raise ValueError("Entity type not supported")

        for entity in entities:
            if not (is_valid(entity)):
                continue

            offset = entity.offset
            length = entity.length
            value = text[offset:offset + length]

            # next values will be ignores
            break

        return value

    def guess_bot_command(self, default=CommandsNames.HELP) -> str:
        """
        Tries to guess which bot command
        user assumed based on a message.

        :param default: Default command which will be
        returned if unable to guess.

        :returns: Guessed bot command based on a message.
        """
        command = default

        if ("photo" in self.raw_data):
            command = CommandsNames.UPLOAD_PHOTO
        elif ("document" in self.raw_data):
            command = CommandsNames.UPLOAD_FILE
        elif ("audio" in self.raw_data):
            command = CommandsNames.UPLOAD_AUDIO
        elif ("video" in self.raw_data):
            command = CommandsNames.UPLOAD_VIDEO
        elif ("voice" in self.raw_data):
            command = CommandsNames.UPLOAD_VOICE

        return command


class Request:
    """
    Incoming Telegram requset through webhook.

    https://core.telegram.org/bots/api/#making-requests
    """
    def __init__(self, raw_data: dict) -> None:
        self.raw_data = raw_data

    def is_valid(self) -> bool:
        """
        :returns: Incoming data is valid for handling.
        """
        return (
            isinstance(
                self.raw_data.get("update_id"),
                int
            ) and
            (
                isinstance(
                    self.raw_data.get("message"),
                    dict
                ) or
                isinstance(
                    self.raw_data.get("edited_message"),
                    dict
                )
            )
        )

    def get_message(self) -> Message:
        """
        :returns: Telegram user message.
        """
        raw_data = (
            self.raw_data.get("message") or
            self.raw_data.get("edited_message")
        )
        message = Message(raw_data)

        return message
